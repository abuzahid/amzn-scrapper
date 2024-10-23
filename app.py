import requests
from bs4 import BeautifulSoup
import streamlit as st
import numpy as np
import pandas as pd
from helper.db import save_to_database
from helper.utils import (
                          get_title, 
                          get_price, 
                          get_specification_data,
                          get_rating,
                          get_review_count,
                          get_availability
                          )


HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
    "Accept-Language": "en-US, en;q=0.5",
}


# Initialize Streamlit interface
st.title("Amazon scrapper")
st.write("Type your keyword")



input = st.text_area("Your search keyword?")
if input is not None:
    button = st.button("Submit")
    search_keyword = '+'.join(part.strip() for part in input.split())
    
    if button:
        try:
            URL = f"https://www.amazon.com/s?k={search_keyword}&crid=3FXH81OBIY0OW&sprefix=watche%2Caps%2C422&ref=nb_sb_noss_2"
            webpage = requests.get(URL, headers=HEADERS, timeout=10)
            
            soup = BeautifulSoup(webpage.content, "html.parser")
            links = soup.find_all("a", attrs={'class':'a-link-normal s-underline-text s-underline-link-text s-link-style a-text-normal'})
            
            links_list = []
            for link in links:
                links_list.append(link.get('href'))
            
            d = {
                "title": [], 
                "price": [], 
                "brand": [], 
                "model": [],
                "rating": [], 
                "reviews": [],
                "availability": []
            }
            
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            # Loop for extracting product details from each link
            for i, link in enumerate(links_list):
                try:
                    new_webpage = requests.get("https://www.amazon.com" + link, headers=HEADERS)
                    new_soup = BeautifulSoup(new_webpage.content, "html.parser")
                    
                    # Get product details using your helper functions
                    brand, model = get_specification_data(new_soup)
                    d['title'].append(get_title(new_soup))
                    d['price'].append(get_price(new_soup))
                    d['brand'].append(brand)
                    d['model'].append(model)
                    d['rating'].append(get_rating(new_soup))
                    d['reviews'].append(get_review_count(new_soup))
                    d['availability'].append(get_availability(new_soup))
                    
                    # Update progress
                    progress = (i + 1) / len(links_list)
                    progress_bar.progress(progress)
                    status_text.text(f"Processing product {i + 1} of {len(links_list)}")
                    
                except Exception as e:
                    st.warning(f"Error processing product {i + 1}: {str(e)}")
                    continue
            
            # Create DataFrame
            amazon_df = pd.DataFrame.from_dict(d)
            amazon_df['title'].replace('', np.nan, inplace=True)
            amazon_df = amazon_df.dropna(subset=['title'])
            
            # Save to CSV
            amazon_df.to_csv("Amazon Data.csv", header=True, index=False)
            
            # Save to database
            save_to_database(amazon_df)
            
            # Display results
            st.success("Data collection completed!")
            st.write("Preview of collected data:")
            st.dataframe(amazon_df)
            
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")