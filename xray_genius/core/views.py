from django.db import transaction
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CTInputFileUploadForm
from .models import Session


def dashboard(request: HttpRequest):
    sessions = Session.objects.filter(owner=request.user)
    return render(request, 'dashboard.html', {'sessions': sessions})


def upload_ct_input_file(request: HttpRequest):
    if request.method == 'POST':
        form = CTInputFileUploadForm(request.POST, request.FILES)
        if form.is_valid():
            with transaction.atomic():
                file = form.save()
                Session.objects.create(owner=request.user, input_scan=file)
            return redirect('dashboard')
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
