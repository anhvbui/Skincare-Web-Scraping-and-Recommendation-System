import time
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import requests
from bs4 import BeautifulSoup


# Step 1: Open website 
driver2 = webdriver.Chrome()
driver2.get('https://oliveyoung.com//')
print(driver2.title)
time.sleep(2)

 # Step 2: Close the 'Are you resident of CA?' window
try:
    resident_YN = WebDriverWait(driver2, 10).until(EC.presence_of_element_located((By.XPATH, "/html/body/div[15]/div[2]/div/div[2]/div/button")) )
    time.sleep(2)
    resident_YN.click()
    print("Cleared 'Are you a CA resident' question")
except:
    print("No resident CA question shown.")


# Step 3: Click the Catergories button -> choose Skincare
categories_button = driver2.find_element(By.LINK_TEXT,"Categories")
categories_button.click()
time.sleep(2)

skincare_button2 = driver2.find_element(By.LINK_TEXT,"Skincare")
skincare_button2.click()
time.sleep(5)

# Step 4: Get total page numbers
more_page_button = driver2.find_element(By.CSS_SELECTOR,".btn-page-more")
driver2.execute_script("arguments[0].scrollIntoView(true)",more_page_button)
pages_text = more_page_button.text
start_index = pages_text.index("/")+1
end_index = len(pages_text)-1
total_pages = int(pages_text[start_index:end_index])
time.sleep(2)

# Step 5: Scroll down to the 'More page' button and click it 'Total_pages' times
for page in range(1):
    try:
        more_page_button = driver2.find_element(By.CSS_SELECTOR,".btn-page-more")
        more_page_button.click()
        time.sleep(2)
        WebDriverWait(driver2, 5).until(EC.presence_of_element_located((By.CLASS_NAME,"unit-list")) )
        
    except Exception as e:
        print(f"Exception: {e}")
        print("Loading page did not complete.")
        break
     
print(f"Loading page {total_pages} completed.")

# Step 6: Extract href links of products 
product_links = []
product_count = 0
all_links = driver2.find_elements(By.TAG_NAME,"a")

for link in all_links:
    all_hrefs = link.get_attribute("href")
    if all_hrefs and "/product/" in all_hrefs:
        product_count += 1
        product_links.append(all_hrefs)

    # Step 6.1: There are 2 href links for each product, so I have to remove duplicates
def distinct(product_links):
    distinct_links = []
    for l in product_links:
        if l not in distinct_links:
            distinct_links.append(l)
    return distinct_links

print(f"All Product links found: ")   
distinct_list = distinct(product_links)
print(distinct_list)
print(f"Total link count: {len(distinct_list)}") 


driver2.quit()
    
