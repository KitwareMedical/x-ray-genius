from collections.abc import Callable
from typing import ParamSpec, TypeVar
from urllib.parse import urlencode

from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied, SuspiciousOperation
from django.db import transaction
from django.db.models import Exists, OuterRef, Subquery
from django.http import HttpRequest, HttpResponseBadRequest
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_http_methods, require_POST
from django_celery_results.models import TaskResult

from .forms import CTInputFileUploadForm
from .models import CTInputFile, SampleDataset, SampleDatasetFile, Session
from .tasks import delete_session_task, run_deepdrr_task

T = TypeVar('T')
P = ParamSpec('P')


def user_has_reached_session_limit(user: User) -> bool:
    if user.is_superuser or user.is_staff:
        # Superusers and staff can start as many sessions as they want
        return False
    return Session.objects.filter(owner=user).count() >= settings.USER_SESSION_LIMIT


def quota_check(view: Callable[P, T]) -> Callable[P, T]:
    def check(request: HttpRequest, *args, **kwargs):
        if user_has_reached_session_limit(request.user):
            raise SuspiciousOperation(
                'User has reached session limit, but tried to start a new session through the API.'
            )
        return view(request, *args, **kwargs)

    return check


def permission_check(view: Callable[P, T]) -> Callable[P, T]:
    def check(request: HttpRequest, *args, **kwargs):
        if session_pk := kwargs.get('session_pk'):
            session = get_object_or_404(Session, pk=session_pk)
            if session.owner != request.user:
                raise Http404()
        return view(request, *args, **kwargs)

    return check


@permission_check
@require_GET
def dashboard(request: HttpRequest):
    sessions = (
        Session.objects.select_related('input_scan', 'parameters')
        .prefetch_related('output_images')
        .filter(owner=request.user)
        .order_by('-created')
        .annotate(
            has_task_result=Subquery(
                Exists(
                    TaskResult.objects.filter(
                        task_id=OuterRef('celery_task_id'),
                    )
                ),
            ),
        )
    )

    # Whether or not the page should refresh every 5 seconds automatically.
    should_refresh = sessions.filter(status=Session.Status.RUNNING).exists()

    return render(
        request,
        'dashboard.html',
        {
            'sessions': sessions,
            'SessionStatus': Session.Status,
            'should_refresh': should_refresh,
            'should_disable_new_session_button': user_has_reached_session_limit(request.user),
        },
    )


@permission_check
@quota_check
@require_http_methods(['GET', 'POST'])
def upload_ct_input_file(request: HttpRequest):
    if request.method == 'POST':
        form = CTInputFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                file = form.save()
                session = Session.objects.create(owner=request.user, input_scan=file)
            # Redirect to VolView viewer with the uploaded file
            return redirect(
                reverse('viewer', kwargs={'session_pk': session.pk})
                + '?'
                + urlencode({'urls': file.file.url})
            )
    else:
        form = CTInputFileUploadForm()
    return render(
        request,
        'upload_ct_file.html',
        {
            'form': form,
            'sample_datasets': SampleDataset.objects.prefetch_related('files'),
        },
    )


@permission_check
@quota_check
@require_POST
def start_session_with_sample_data(request: HttpRequest, sample_dataset_file_pk: int):
    sample_dataset = get_object_or_404(SampleDatasetFile, pk=sample_dataset_file_pk)
    with transaction.atomic():
        ct_input_file = CTInputFile.objects.create(file=sample_dataset.file)
        session = Session.objects.create(owner=request.user, input_scan=ct_input_file)
        return redirect(
            reverse('viewer', kwargs={'session_pk': session.pk})
            + '?'
            + urlencode({'urls': ct_input_file.file.url})
        )


@permission_check
@require_POST
def delete_session(request: HttpRequest, session_pk: str):
    # Only staff and superusers can delete sessions
    if not request.user.is_staff and not request.user.is_superuser:
        raise SuspiciousOperation('Non-admin attempted to delete a session.')

    with transaction.atomic():
        session = get_object_or_404(Session.objects.select_for_update(), pk=session_pk)
        session.status = Session.Status.DELETING
        session.save()
    delete_session_task.delay(session_pk)
    return redirect('dashboard')


@permission_check
@require_GET
def download_ct_file(request: HttpRequest, session_pk: str):
    session = get_object_or_404(Session, pk=session_pk)
    return redirect(session.input_scan.file.url)


@permission_check
@require_GET
def volview_viewer(request: HttpRequest, session_pk: str):
    session = get_object_or_404(Session, pk=session_pk)
    return render(request, 'viewer.html', context={'session': session})


@permission_check
@quota_check
@require_POST
def initiate_batch_run(request: HttpRequest, session_pk: str):
    with transaction.atomic():
        session = get_object_or_404(Session.objects.select_for_update(), pk=session_pk)
        if not session.parameters:
            # Error: parameters missing. The UI should prevent this from ever happening.
            return HttpResponseBadRequest('Parameters missing')
        elif session.status not in (Session.Status.NOT_STARTED, Session.Status.CANCELLED):
            return HttpResponseBadRequest('Invalid start state.')
        session.status = Session.Status.RUNNING
        session.save()
    task = run_deepdrr_task.delay(session_pk)
    Session.objects.filter(pk=session_pk).update(celery_task_id=task.id)
    return redirect('dashboard')


@permission_check
@require_POST
def cancel_batch_run(request: HttpRequest, session_pk: str):
    with transaction.atomic():
        session = get_object_or_404(Session.objects.select_for_update(), pk=session_pk)
        session.status = Session.Status.CANCELLED
        session.save()
    return redirect('dashboard')


@require_GET
def get_task_trace(request: HttpRequest, session_pk: str):
    # Only staff and superusers can view task info, regardless of
    # who owns the session.
    if not request.user.is_staff and not request.user.is_superuser:
        raise PermissionDenied()
    session = get_object_or_404(Session, pk=session_pk)
    task_result = get_object_or_404(TaskResult, task_id=session.celery_task_id)
    return render(
        request,
        'task_trace.html',
        context={
            'task_result': task_result,
        },
    )
