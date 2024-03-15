from collections.abc import Callable
from typing import ParamSpec, TypeVar
from urllib.parse import urlencode

from django.db import transaction
from django.http import HttpRequest, HttpResponseBadRequest
from django.http.response import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import CTInputFileUploadForm
from .models import Session
from .tasks import run_deepdrr_task

T = TypeVar('T')
P = ParamSpec('P')


def permission_check(view: Callable[P, T]) -> Callable[P, T]:
    def check(request: HttpRequest, *args, **kwargs):
        if session_pk := kwargs.get('session_pk'):
            session = get_object_or_404(Session, pk=session_pk)
            if session.owner != request.user:
                raise Http404()
        return view(request, *args, **kwargs)

    return check


@permission_check
def dashboard(request: HttpRequest):
    sessions = Session.objects.filter(owner=request.user).order_by('-created')

    # Whether or not the page should refresh every 5 seconds automatically.
    should_refresh = sessions.filter(status=Session.Status.RUNNING).exists()

    return render(
        request,
        'dashboard.html',
        {
            'sessions': sessions,
            'SessionStatus': Session.Status,
            'should_refresh': should_refresh,
        },
    )


@permission_check
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
        },
    )


@permission_check
def download_ct_file(request: HttpRequest, session_pk: str):
    session = get_object_or_404(Session, pk=session_pk)
    return redirect(session.input_scan.file.url)


@permission_check
def volview_viewer(request: HttpRequest, session_pk: str):
    session = get_object_or_404(Session, pk=session_pk)
    return render(request, 'viewer.html', context={'session': session})


@permission_check
@require_POST
def initiate_batch_run(request: HttpRequest, session_pk: str):
    with transaction.atomic():
        session = get_object_or_404(Session.objects.select_for_update(), pk=session_pk)
        if not session.parameters:
            # Error: parameters missing. The UI should prevent this from ever happening.
            return HttpResponseBadRequest('Parameters missing')
        elif session.status != Session.Status.NOT_STARTED:
            return HttpResponseBadRequest('Invalid start state.')
        session.status = Session.Status.RUNNING
        session.save()
    run_deepdrr_task.delay(session_pk)
    return redirect('dashboard')
