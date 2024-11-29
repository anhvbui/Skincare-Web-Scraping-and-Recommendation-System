from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import TestUser
from .forms import CreateUserForm


# Create your views here.
def homepage(request):
    context = {}
    return render(request,"homepage.html", context)

def loginPage(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('homepage')
        else:
            messages.info(request, 'Username or password is incorrect.')
    context = {}
    return render(request,"login.html", context)

def logoutPage(request):
    logout(request)
    return redirect('homepage')

def signup(request):
    form = CreateUserForm()
    if request.method == "POST":
        form = CreateUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Created an Account Successfully.")
    context = {'form':form}
    return render(request,"signup.html", context)

def test(request):
    obj = TestUser.objects.all()
    context = {
        "obj": obj,
    }
    return render(request, "test.html", context)

@login_required(login_url='login')
def skinQuiz(request):
    context = {}
    return render(request,"skin-quiz.html", context)

@login_required(login_url='login')
def quizResult(request):
    context = {}
    return render(request,"quiz-result.html", context)
