#import os
#import django
import pandas as pd
import numpy as np
import ast
#from ..views import quizResult


# Set up Django settings
#os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.myproject.settings')
#django.setup()




def create_bow(att_list):
    if isinstance(att_list, str):
        att_list = att_list.split(', ')
    elif not hasattr(att_list, '__iter__'):
        return {}

    freq = {}
    for att in att_list:
        if att not in freq:
            freq[att] = 0
        freq[att] += 1
    return freq

def att_probability(att_list):
    if isinstance(att_list, str):
        att_list = att_list.split(', ')
    elif not hasattr(att_list, '__iter__'):
        return {}

    att_prob = {}
    for att in att_list:
        if att not in att_prob:
            att_prob[att] = 0
        att_prob[att] += 1 / len(att_list)
    return att_prob

# Clean data
def clean_user_data(user_df):
    for col in ['user_skin_type', 'user_skin_concerns']:
        user_df[col] = user_df[col].str.replace('[', '').str.replace(']', '').str.replace("'", '')
    return user_df

def load_user_submission():
    new_user_data = {
              'user_id': [1,2,3,4,5],
              'routine_steps': ['6+','6+','1-3','1-3','4-5'],
              'Dry': [1,0,0,0,0],
              'Sensitive': [0,1,0,0,0],
              'Oily': [0,0,1,0,0],
              'Combination': [0,0,0,1,0],
              'Normal': [0,0,0,0,1],
              'Acne': [0, 0.15, 0.4, 0.27, 0.06],
              'Blackheads': [0.1, 0, 0.3, 0.25, 0.28],
              'Brightening': [0, 0, 0, 0.6, 0.5],
              'Sun Care': [1, 1, 1, 0.5, 0],
              'Moisturising': [1, 0.5, 0.18, 0.4, 0.39],
              'Dullness': [0.44, 0.05, 0, 0, 0.21],
              'Soothing': [0.3, 0.33, 0.07, 0.2, 0.07],
              'Stress': [0.01, 1, 0, 0.5, 0.35],     # same as sensitivity
              'Visible Pores': [0.1, 0, 0.3, 0.25, 0.28], # same as blackheads
              'Well-aging': [1, 0.5, 0, 0.5, 0],       # same as wrinkle
              'Sculpting': [1, 0.5, 0, 0.5, 0],        # same as well-aging
              'Puffiness': [0, 0, 0, 0.2, 0.81],
              'Scarring': [0, 0.7, 0.7, 0, 0],
              }
    
    new_user_df = pd.DataFrame(new_user_data)
    return new_user_df

# Generate recommendations
def generate_recommendations(user_id, user_df, product_df, user_submission):
    rating_avg = product_df['rating'].mean(skipna=True)
    review_count_avg = product_df['reviews_no'].mean(skipna=True)

    # Prepare data
    cleaned_user_data = clean_user_data(user_df)
    skin_types = user_df['user_skin_type'].tolist()
    skin_concerns = user_df['user_skin_concerns'].tolist()
    prod_names = user_df['prod_name'].tolist()
    
    #Prepare skin type data
    skin_type_bow = [create_bow(skin_type) for skin_type in skin_types]
    skin_types_df = pd.DataFrame(skin_type_bow, index=prod_names).fillna(0)
    skin_type_prob = [att_probability(skin_type) for skin_type in skin_types]
    skin_types_prob_df = pd.DataFrame(skin_type_prob, index=prod_names).fillna(0)

    #Prepare skin concern data
    skin_concerns_bow = [create_bow(skin_concern) for skin_concern in skin_concerns]
    skin_concerns_df = pd.DataFrame(skin_concerns_bow, index=prod_names).fillna(0)
    skin_concerns_df['item_no'] = np.arange(len(skin_concerns_df))
    skin_concerns_df.drop(['B', 'M', 'Scarri', 'Bl', 'Brighteni', 'Brightening,'], axis=1, inplace=True)
    skin_concerns_prob = [att_probability(skin_concern) for skin_concern in skin_concerns]
    skin_concerns_prob_df = pd.DataFrame(skin_concerns_prob, index=prod_names).fillna(0)
    skin_concerns_prob_df.drop(['B', 'M', 'Scarri', 'Bl', 'Brighteni', 'Brightening,'], axis=1, inplace=True)
    

    combined_product_df = pd.concat([skin_concerns_prob_df, skin_types_prob_df], axis=1).fillna(0)
    combined_product_df.drop(['','Fine Dust Removal','Slimming','Stretch Marks','Cellulite','Ac','Visibl','Brightenin'], axis=1, inplace=True)
    combined_product_df = combined_product_df[sorted(combined_product_df.columns)]
    #print("Combined product df:", combined_product_df)
    #print(combined_product_df.head(10))
    print(f"Row count of all products DF before recommendation filter: {combined_product_df.shape[0]}")
    combined_col_names = combined_product_df.columns
    #print("Combined product data's column list: ",combined_col_names)
    
    # Prepare product & user data matrix
    #new_user_df = load_user_submission()
    trimmed_new_user_df = user_submission.drop(['age', 'user_id', 'routine_steps', 'Dryness'], axis=1)
    trimmed_new_user_df = trimmed_new_user_df[sorted(trimmed_new_user_df.columns)]
    user_sub_col_names = trimmed_new_user_df.columns
    print(user_sub_col_names)


    U = trimmed_new_user_df.to_numpy()
    P = combined_product_df.to_numpy()

    # Calculate similarity scores
    S = np.dot(U, P.T)
    user_scores = S[user_id - 1]

    # Filter recommendations
    recommendations_df = pd.DataFrame({
        'similarity_score': user_scores,
        'prod_name': product_df['prod_name'],
        'brand': product_df['brand'],
        'ingredients': product_df['ingredients'],
        'price': product_df['price'],
        'category': product_df['category'],
        'subcategory': product_df['subcategory'],
        'rating': product_df['rating'],
        'reviews_no': product_df['reviews_no'],
        'link':product_df['link']
    })
    recommendations_df = recommendations_df[
        (recommendations_df['rating'] >= rating_avg) &
        (recommendations_df['reviews_no'] > review_count_avg * 2)
    ]
    recommendations_df = recommendations_df.sort_values(by='similarity_score', ascending=False)
    #recommendations_df = recommendations_df.drop_duplicates(subset=['subcategory'], keep='first')
    return recommendations_df


# Simple routine-based recommendations
def routine_based_recommendations(preferred_product_no, product_df):
    df_cleanser = product_df[(product_df['category'] == 'Cleansers') & (product_df['rating'] >= product_df['rating'].mean())]
    df_toner = product_df[(product_df['category'] == 'Moisturizers') & (product_df['subcategory'] == 'Toner')]
    df_serum = product_df[(product_df['category'] == 'Moisturizers') & (product_df['subcategory'] == 'Essence & Serum')]
    df_moisturizer = product_df[(product_df['category'] == 'Moisturizers') & (product_df['subcategory'].isin(['Moisturizer', 'Cream']))]

    if preferred_product_no <= 3:
        random_cleanser = df_cleanser.sample(n=1)['prod_name'].values[0]
        random_moisturizer = df_moisturizer.sample(n=1)['prod_name'].values[0]
        return [random_cleanser, random_moisturizer]
    elif 3 < preferred_product_no <= 5:
        random_cleanser = df_cleanser.sample(n=1)['prod_name'].values[0]
        random_toner = df_toner.sample(n=1)['prod_name'].values[0]
        random_serum = df_serum.sample(n=1)['prod_name'].values[0]
        random_moisturizer = df_moisturizer.sample(n=1)['prod_name'].values[0]
        return [random_cleanser, random_toner, random_serum, random_moisturizer]


def load_product_data():
    return pd.read_excel(r'C:\Users\buiva\OneDrive\Documents\GitHub\Web-scraping-Selenium-test\myproject\app\data\ProductData-Master-Completed.xlsx')

def load_user_data():
    return pd.read_excel(r'C:\Users\buiva\OneDrive\Documents\GitHub\Web-scraping-Selenium-test\myproject\app\data\UserData-Master-Completed.xlsx')


# Example for testing outside Django)
if __name__ == "__main__":
    # Load data
    product_df = load_product_data()
    user_df = load_user_data()

    # Recommendations
    #user_info = quizResult() 
    #user_id = user_info['user_id']  
    #recommendations = generate_recommendations(user_id, user_df, product_df)
    #print(recommendations.head())

    #preferred_product_no =  user_info['routine_steps'] # Replace with user input
    #routine_recommendations = routine_based_recommendations(preferred_product_no, product_df)
    #print(routine_recommendations)
