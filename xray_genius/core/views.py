from django.db import transaction
from django.http import HttpRequest, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from xray_genius.core.tasks import run_deepdrr_task

from .forms import CTInputFileUploadForm
from .models import Session


def dashboard(request: HttpRequest):
    sessions = Session.objects.filter(owner=request.user)
    return render(
        request,
        'dashboard.html',
        context={
            'sessions': sessions,
            'SessionStatus': Session.Status,
        },
    )


def upload_ct_input_file(request: HttpRequest):
    if request.method == 'POST':
        form = CTInputFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                file = form.save()
                session = Session.objects.create(owner=request.user, input_scan=file)
            return redirect('viewer', session_pk=session.pk)
    else:
        form = CTInputFileUploadForm()
    return render(
        request,
        'upload_ct_file.html',
        {
            'form': form,
        },
    )


def download_ct_file(request: HttpRequest, session_pk: str):
    session = get_object_or_404(Session, pk=session_pk)
    return redirect(session.input_scan.file.url)


def volview_viewer(request: HttpRequest, session_pk: str):
    session = get_object_or_404(Session, pk=session_pk)
    return render(request, 'viewer.html', context={'session': session})


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
