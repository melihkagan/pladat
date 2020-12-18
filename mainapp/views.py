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
    return render(request, "index.html")

@login_required
def employer(request):
    return render(request, "employer.html")

@login_required
def view_self_profile(request, username=None):
    print(username)
    # obj = get_object_or_404(PostModel, id=id)
    if request.user.is_authenticated:
        context = {
            "object": User
        }
    username = request.user.username
    print(username)
    template = "profile.html"
    return render(request, template, {"username": username})

@login_required
def add_skill(request):
    # obj = get_object_or_404(PostModel, id=id)
    template = "addskill.html"
    return render(request, template)

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