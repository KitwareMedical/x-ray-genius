from django.shortcuts import render, redirect
from django.http import HttpRequest
from django.db import transaction
from .models import Session, CTInputFile
from .forms import CTInputFileUploadForm


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
