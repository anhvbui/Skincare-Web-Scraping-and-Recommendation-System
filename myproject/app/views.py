from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.http import JsonResponse

from .models import TestUser
from .forms import CreateUserForm

import json


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
    #fetch the submission array from the main.js file using Fetch API
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            #print(f"JS Original fetched data: {data}")
            user_data = data.get('post_data', [])
            to_be_processed = skin_concern_weight(user_data)
            #print(f"User Data: {user_data}")  # Debugging to see the output of the function
            processed_data = assign_att_score(to_be_processed, request)
            messages.success(request, "User Information Submitted.")
            return redirect(reverse('quiz-result'))
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            # Catch any other errors
            return JsonResponse({'error': str(e)}, status=450)
    else:
        return render(request, "skin-quiz.html", context)

def assign_att_score(to_be_processed, request):
    user_input = {
              'user_id': None,
              'routine_steps': None,
              'age': None,
              'Dry': 0,
              'Sensitive': 0,
              'Oily': 0,
              'Combination': 0,
              'Normal': 0,
              'Acne': 0,
              'Blackheads': 0,
              'Brightening': 0,
              'Sun Care': 0,
              'Moisturising': 0,
              'Dullness': 0,
              'Soothing': 0,   # same as sensitivity
              'Stress': 0,     # same as uneven texture
              'Visible Pores': 0, # same as blackheads
              'Well-aging': 0,       # same as wrinkle
              'Sculpting': 0,        # same as well-aging
              'Puffiness': 0,
              'Scarring': 0,
              }
    
    if request.user.is_authenticated:
        current_user_id = request.user.id
        user_input['user_id'] = current_user_id
    
    for item in to_be_processed:
        if item['name'] == 'routine_steps':
            user_input['routine_steps'] = int(item['value'])
        if item['name'] == 'age':
            user_input['age'] = item['value']
    
    skin_type_result = skin_type_weight(to_be_processed)
    user_input.update(skin_type_result)

    skin_concern_result = skin_concern_weight(to_be_processed)
    user_input.update(skin_concern_result)

    print(f"Original sensitivity score: {user_input['Soothing']}")
    print(f"Original sun care score: {user_input['Sun Care']}")
    # Make final adjusments based on user input
    for item in to_be_processed:
        if item['name'] == 'sensitivity_adj':
            user_input['Soothing'] += float(item['value'])
            print(f"Updated sensitivity score: {user_input['Soothing']}")
        if item['name'] == 'sun_care_adj':
            user_input['Sun Care'] += float(item['value'])
            print(f"Updated sun care score: {user_input['Sun Care']}")
            
            
    print(f"User input to feed to Google Colab later: {user_input}")
    return user_input



def skin_concern_weight(to_be_processed):
    skin_concerns = {
            'Acne': 0,
            'Blackheads': 0,
            'Brightening': 0,
            'Sun Care': 0,
            'Moisturising': 0,
            'Dullness': 0,
            'Soothing': 0,
            'Stress': 0,     # same as sensitivity
            'Visible Pores': 0, # same as blackheads
            'Well-aging': 0,       # same as wrinkle
            'Sculpting': 0,        # same as well-aging
            'Puffiness': 0,
            'Scarring': 0,
            }
    
    # Iterate over the incoming data to collect values for 'skin_concerns'
    selected_concerns = [item['value'] for item in to_be_processed if item['name'] == 'skin_concerns']
            
    key_count = len(selected_concerns)
    if key_count > 0:
        dist_weight = 1/key_count
    else: 0
    
    for item in selected_concerns:
        skin_concerns[item] = dist_weight

    return skin_concerns

def skin_type_weight(to_be_processed):
    skin_types = {
            'Dry': None,
            'Sensitive': None,
            'Oily': None,
            'Combination': None,}
    skin_types = {key: 0 for key in skin_types.values()}

    for item in to_be_processed:
        if item['name'] == 'skin_type':  
            type = item['value']
            if type:
                skin_types[type] = 1  

    return skin_types



#def user_data_model():



@login_required(login_url='login')
def quizResult(request):
    context = {}
    return render(request,"quiz-result.html", context)
