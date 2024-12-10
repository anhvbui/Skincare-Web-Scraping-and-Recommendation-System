import pandas as pd
import numpy as np
import ast


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

# Generate recommendations
def generate_recommendations(user_id, user_df, product_df):
    rating_avg = product_df['rating'].mean(skipna=True)
    review_count_avg = product_df['reviews_no'].mean(skipna=True)

    # Prepare data
    skin_types = user_df['user_skin_type'].tolist()
    skin_concerns = user_df['user_skin_concerns'].tolist()
    prod_names = user_df['prod_name'].tolist()

    skin_type_prob = [att_probability(skin_type) for skin_type in skin_types]
    skin_concerns_prob = [att_probability(skin_concern) for skin_concerns in skin_concerns]

    skin_types_prob_df = pd.DataFrame(skin_type_prob, index=prod_names).fillna(0)
    skin_concerns_prob_df = pd.DataFrame(skin_concerns_prob, index=prod_names).fillna(0)

    combined_product_df = pd.concat([skin_concerns_prob_df, skin_types_prob_df], axis=1).fillna(0)

    # Prepare user data matrix
    trimmed_new_user_df = user_df.drop(['user_id', 'routine_steps'], axis=1)
    U = trimmed_new_user_df.to_numpy()
    P = combined_product_df.to_numpy()

    # Calculate similarity scores
    S = np.dot(U, P.T)
    user_scores = S[user_id - 1]

    # Filter recommendations
    recommendations_df = pd.DataFrame({
        'similarity_score': user_scores,
        'prod_name': product_df['prod_name'],
        'category': product_df['category'],
        'subcategory': product_df['subcategory'],
        'rating': product_df['rating'],
        'reviews_no': product_df['reviews_no']
    })
    recommendations_df = recommendations_df[
        (recommendations_df['rating'] >= rating_avg) &
        (recommendations_df['reviews_no'] > review_count_avg * 2)
    ]
    recommendations_df = recommendations_df.sort_values(by='similarity_score', ascending=False)
    recommendations_df = recommendations_df.drop_duplicates(subset=['subcategory'], keep='first')
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

# Example usage (for testing outside Django)
if __name__ == "__main__":
    # Load data
    product_df = pd.read_excel(r'C:\Users\buiva\OneDrive\Documents\GitHub\Web-scraping-Selenium-test\myproject\app\data\ProductData-Master-Completed.xlsx')
    user_df = pd.read_excel(r'C:\Users\buiva\OneDrive\Documents\GitHub\Web-scraping-Selenium-test\myproject\app\data\UserData-Master-Completed.xlsx')

    # Recommendations
    user_id = 1  # 
    recommendations = generate_recommendations(user_id, user_df, product_df)
    print(recommendations.head())

    preferred_product_no = 4  # Replace with user input
    routine_recommendations = routine_based_recommendations(preferred_product_no, product_df)
    print(routine_recommendations)
