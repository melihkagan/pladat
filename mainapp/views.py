from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
# Create your views here.

def landing(request):
    return render(request, 'landing.html')

@login_required
def index(request):
    return render(request,"index.html")

@login_required
def employer(request):
    return render(request,"employer.html")

@login_required
def profile(request):
    return render(request,"profile.html")

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {
        'form': form
    })

@login_required
def login(request):
    return redirect('index.html')
    