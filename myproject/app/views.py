from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.sessions.models import Session
from django.db import connection
from django.http import JsonResponse
import pandas as pd

from .models import TestUser
from .models import SavedProduct
from .forms import CreateUserForm

import json
from app.utilities import product_recommender

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
            print(f"JS Original fetched data: {data}")
            user_data = data.get('post_data', [])
            print(f"Post data from Js: {user_data}")
            #to_be_processed = skin_concern_weight(user_data)
            #print(f"To be processed: {to_be_processed}")  # Debugging to see the output of the function
            processed_data = assign_att_score(user_data, request)
            print(f"Processed: {processed_data}")
            request.session['processed_user_data'] = processed_data
            #print("Session temporarily stored data:", request.session['processed_user_data'])
            #messages.success(request, "User Information Submitted.")
            redirect_url = reverse('quiz-result')  # URL for the redirect
            return JsonResponse({'status': 'success', 'redirect_url': redirect_url})
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format'}, status=400)
        except Exception as e:
            # Catch any other errors
            print(f"Error encountered: {e}")  # Add this line
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
    print(f"Original dryness score: {user_input['Dry']}")
    
    # Make final adjusments based on user input
    for item in to_be_processed:
        if item['name'] == 'sensitivity_adj':
            user_input['Soothing'] += float(item['value'])
            print(f"Updated sensitivity score: {user_input['Soothing']}")
        if item['name'] == 'sun_care_adj':
            user_input['Sun Care'] += float(item['value'])
            print(f"Updated sun care score: {user_input['Sun Care']}")
        if item['name'] == 'Dryness':
            user_input['Dry'] += 0.3
            print(f"Updated sun care score: {user_input['Dry']}")
        
            
            
    print(f"User input to feed to product recommender: {user_input}")
    return user_input



def skin_concern_weight(to_be_processed):
    skin_concerns = {
            'Acne': 0,
            'Blackheads': 0,
            'Brightening': 0,
            'Sun Care': 0,
            'Moisturising': 0,
            'Dullness': 0,
            'Dryness': 0,
            'Soothing': 0,
            'Stress': 0,     # same as sensitivity
            'Visible Pores': 0, # same as blackheads
            'Well-aging': 0,       # same as wrinkle
            'Sculpting': 0,        # same as well-aging
            'Puffiness': 0,
            'Scarring': 0,
            'Oily': 0
            }
    
    # Iterate over the incoming data to collect values for 'skin_concerns'
    selected_concerns = [item['value'] for item in to_be_processed if item['name'] == 'skin_concerns']
            
    key_count = len(selected_concerns)
    if key_count > 0:
        dist_weight = 1/key_count
    else: 0
    
    for item in selected_concerns:
        if item in skin_concerns:
            skin_concerns[item] = dist_weight
        else:
            dist_weight = 0
            print(f"Warning: {item} not found in skin_concerns.")

    return skin_concerns

def skin_type_weight(to_be_processed):
    skin_types = {
            'Dry': 0,
            'Sensitive': 0,
            'Oily': 0,
            'Combination': 0,}

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
    finalized_user_data = request.session.get('processed_user_data', None)
    print(f"Session data retrieved:{finalized_user_data}")

    """
    # test
    context['recommendations'] = [
    {'prod_name': 'Alice', 'brand': 'Cosrx', 'price': 25.00, 'category': 'moisturizer', 'subcategory': 'cream', 'rating': 4.8, 'reviews_no': 346, 'link': 'www.google.com'},
    {'prod_name': 'Bob', 'brand': 'Laneige', 'price': 46.00, 'category': 'cleanser', 'subcategory': 'cleansing oil', 'rating': 4.8, 'reviews_no': 89, 'link': 'www.google.com'},
    {'prod_name': 'Dan', 'brand': 'Aestura', 'price': 7.50, 'category': 'serum', 'subcategory': 'serum', 'rating': 4.8, 'reviews_no': 2083, 'link': 'www.google.com'},
    {'prod_name': 'Lily', 'brand': 'Dr.G', 'price': 19.00, 'category': 'sunscreen', 'subcategory': '', 'rating': 4.8, 'reviews_no': 239, 'link': 'www.google.com'}
    ]

    return render(request,"quiz-result.html", context)
    """

    user_df = product_recommender.load_user_data()
    product_df = product_recommender.load_product_data()
    if finalized_user_data is not None:
        user_submission = finalized_user_data
        print("Verify user submission: ", user_submission)
        id = user_submission['user_id']
        user_submission_df = pd.DataFrame([user_submission])
        print(user_submission_df.shape[0])
        product_recs = product_recommender.generate_recommendations(id, user_df, product_df, user_submission_df)
        print(f"Row count of product recommendation DF: {product_recs.shape[0]}")
        if not product_recs.empty:
            user_routine_steps = user_submission['routine_steps']
            prod_list = []
            df_cleansing_oil = product_recs[(product_recs['category'] == 'Cleansers') & (product_recs['subcategory'] == 'Cleansing Oil')]
            df_cleansing_foam = product_recs[(product_recs['category'] == 'Cleansers') & (product_recs['subcategory'] == 'Cleansing Foam')]
            df_toner = product_recs[(product_recs['category'] == 'Moisturizers') & (product_recs['subcategory'] == 'Toner')]
            df_serum = product_recs[(product_recs['category'] == 'Moisturizers') & (product_recs['subcategory'] == 'Essence & Serum')]
            df_moisturizer = product_recs[(product_recs['category'] == 'Moisturizers') & ((product_recs['subcategory'] == 'Moisturizer') | (product_recs['subcategory'] == 'Cream'))]
            df_sunscreen = product_recs[(product_recs['category'] == 'Sunscreen')]

            if user_routine_steps <= 3:
                print("User routine step is 3.")
                prod_list.append(df_cleansing_foam.head(1).to_dict(orient='records'))
                prod_list.append(df_moisturizer.head(1).to_dict(orient='records'))
                prod_list.append(df_sunscreen.head(1).to_dict(orient='records'))
            elif user_routine_steps > 3 and user_routine_steps <= 5:
                print("User routine step is 4.")
                prod_list.append(df_cleansing_foam.head(1).to_dict(orient='records'))
                prod_list.append(df_serum.head(1).to_dict(orient='records'))
                prod_list.append(df_moisturizer.head(1).to_dict(orient='records'))
                prod_list.append(df_sunscreen.head(1).to_dict(orient='records'))
            elif user_routine_steps > 5:
                print("User routine step is 6.")
                prod_list.append(df_cleansing_oil.head(1).to_dict(orient='records'))
                prod_list.append(df_cleansing_foam.head(1).to_dict(orient='records'))
                prod_list.append(df_toner.head(1).to_dict(orient='records'))
                prod_list.append(df_serum.head(1).to_dict(orient='records'))
                prod_list.append(df_moisturizer.head(1).to_dict(orient='records'))
                prod_list.append(df_sunscreen.head(1).to_dict(orient='records'))
            
            #top_10_recs = product_recs.head(10).to_dict(orient='records')
            #print(f"Product recs: {prod_list}")
            flat_prod_list = [item for sublist in prod_list for item in sublist]
            context['recommendations'] = flat_prod_list
            #print(f"Test context: {context}")

            request.session['products_data'] = flat_prod_list
        if request.method =="POST":
            products_to_save = request.session.get('products_data', [])

            if products_to_save:
                if request.user.is_authenticated:
                    for product in products_to_save: 
                        prod_name = product.get('prod_name')
                        brand = product.get('brand')
                        price = product.get('price')
                        category = product.get('category')
                        subcategory = product.get('subcategory')
                        rating = product.get('rating')
                        reviews_no = product.get('reviews_no')
                        link = product.get('link')

                        # Save product to database
                        SavedProduct.objects.create(
                            user=request.user,
                            prod_name=prod_name,
                            brand=brand,
                            category=category,
                            subcategory=subcategory,
                            link=link
                        )
                        print(f"Saved products: {prod_name}")
                else: print("User is not authenticated.")
            # Clear the session data after saving
            del request.session['products_data']

    return render(request,"quiz-result.html", context)


def savedItems(request):
    context = {}
    if request.user.is_authenticated:
        user_id = request.user.id
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT id, prod_name, category, subcategory, brand, link, 
                       DATE_TRUNC('minute', created_at) AS created_at_minute
                FROM app_savedproduct
                WHERE user_id = %s
                GROUP BY id, created_at_minute, prod_name, category, subcategory, brand, link
                ORDER BY created_at_minute DESC
            """, [user_id])
            rows = cursor.fetchall()
        
        # Process rows into a dictionary or directly pass to the context
        saved_products = [
            {
                'id': row[0],
                'prod_name': row[1],
                'category': row[2],
                'subcategory': row[3],
                'brand': row[4],
                'link': row[5],
                'created_at_minute': row[6]
            }
            for row in rows
        ]
        context['saved_products'] = saved_products
    else:
        context['error_message'] = "You need to log in to view saved items."
    
    return render(request, "saved-items.html", context)