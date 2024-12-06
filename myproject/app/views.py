from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sessions.models import Session

from .models import TestUser
from .forms import CreateUserForm



# Create your views here.
def homepage(request):
    context = {}
    return render(request,"homepage.html", context)


def loginPage(request):
    if request.user.is_authenticated:
        return redirect('homepage')
    
    if request.method == "POST":
        username = request.POST.get('username','')
        password = request.POST.get('password','')
        print(f"Username: {username}, Password: {password}")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            print(f"User is authenticated after login: {request.user.is_authenticated}")
            print(f"User ID: {user.id}")
            return redirect('homepage')
        else:
            messages.info(request, 'Username or password is incorrect.')
            context = {}
            return render(request,"login.html", context)
    return render(request,"login.html", {})


'''
def loginPage(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            request.session.cycle_key()
            return redirect('homepage')  # replace 'homepage' with your actual homepage URL
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})
    else:
        return render(request, 'login.html')
'''

def logoutPage(request):
    logout(request)
    request.session.clear()
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
    return render(request,"test.html", context)

@login_required(login_url='login')
def skinQuiz(request):
    context = {}
    if request.method == "POST":
        messages.success(request, "User Information Submitted.")
        return redirect(reverse('quiz-result'))
    return render(request,"skin-quiz.html", context)

@login_required(login_url='login')
def quizResult(request):
    context = {}
    return render(request,"quiz-result.html", context)
