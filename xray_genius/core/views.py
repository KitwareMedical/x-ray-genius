from django.shortcuts import render
from django.http import HttpRequest

from .models import Session


def dashboard(request: HttpRequest):
    sessions = Session.objects.filter(owner=request.user)
    return render(request, 'dashboard.html', {'sessions': sessions})
