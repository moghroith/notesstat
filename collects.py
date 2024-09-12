import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from collections import Counter
import logging
import cloudscraper

# Set up logging
logging.basicConfig(level=logging.INFO)

def fetch_with_rate_limit(url, headers=None):
    if headers is None:
        headers = {}
    
    headers.update({
        '_gorilla_csrf': 'your_csrf_token',
        'access_token': 'your_access_token',
        'cf_clearance': 'your_cf_clearance_token',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.yodayo.com'  # Adjust this URL as needed
    })
    
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url, headers=headers)
    
    if response.status_code == 200:
        return response.json()
    else:
        logging.error(f"Failed to fetch data: {response.status_code}")
        return None

def fetch_data(user_id, offset=0, limit=500):
    url = f"https://api.yodayo.com/v1/users/{user_id}/notes?offset={offset}&limit={limit}"
    return fetch_with_rate_limit(url)

def analyze_data(data):
    posts = data.get('posts', [])
    
    total_posts = len(posts)
    total_likes = sum(post['likes'] for post in posts)
    
    names = [post['profile']['name'] for post in posts if 'profile' in post and 'name' in post['profile']]
    name_counts = Counter(names)
    
    df = pd.DataFrame(posts)
    
    return {
        'total_posts': total_posts,
        'total_likes': total_likes,
        'name_counts': name_counts,
        'df': df
    }

def main():
    st.title("Yodayo Collected Post Analyzer")
    
    user_id = st.text_input("Enter User ID")
    
    if st.button("Analyze"):
        all_data = []
        offset = 0
        
        with st.spinner("Fetching data..."):
            while True:
                data = fetch_data(user_id, offset)
                if data is None:
                    st.error("Failed to fetch data. Please check your authentication details and try again.")
                    return
                posts = data.get('posts', [])
                if not posts:
                    break
                all_data.extend(posts)
                offset += len(posts)
                st.text(f"Fetched {len(all_data)} posts so far...")
        
        # Filter out duplicate posts by uuid
        unique_posts = {post['uuid']: post for post in all_data}.values()
        
        if unique_posts:
            st.success(f"Data fetched successfully. Total unique posts: {len(unique_posts)}")
            
            combined_data = {'posts': list(unique_posts)}
            analysis = analyze_data(combined_data)
            
            st.header("Basic Statistics")
            st.write(f"Total Posts: {analysis['total_posts']}")
            st.write(f"Total Likes: {analysis['total_likes']}")
            
            st.subheader("Name Statistics")
            name_df = pd.DataFrame.from_dict(analysis['name_counts'], orient='index', columns=['Count'])
            name_df = name_df.sort_values('Count', ascending=False)
            st.write(f"Total Unique Users Collected From: {len(name_df)}")
            st.write("№ of posts collected from each user:")
            st.dataframe(name_df)
            
            st.header("Post Analysis")
            df = analysis['df']
            
            fig = px.histogram(df, x='likes', title='Distribution of Likes for Collected Posts')
            st.plotly_chart(fig)
            
            st.subheader("Top 10 Most Liked Posts Collected")
            st.dataframe(df.nlargest(10, 'likes')[['title', 'likes']])
            
            df['created_at'] = pd.to_datetime(df['created_at'])
            fig = px.scatter(df, x='created_at', y='likes', title='Creation time of Collected posts')
            st.plotly_chart(fig)
            
        else:
            st.error("No data found for the given user ID.")

if __name__ == "__main__":
    main()
