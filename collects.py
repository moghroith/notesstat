import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px
from collections import Counter

def fetch_data(user_id, offset=0, limit=500):
    url = f"https://api.yodayo.com/v1/users/{user_id}/notes?offset={offset}&limit={limit}&width=600&include_nsfw=true"
    response = requests.get(url)
    return response.json()

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
                posts = data.get('posts', [])
                if not posts:
                    break
                all_data.extend(posts)
                offset += len(posts)
        
        if all_data:
            st.success(f"Data fetched successfully. Total collected posts: {len(all_data)}")
            
            combined_data = {'posts': all_data}
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
            
            st.subheader("Content Rating Distribution for Collected Posts")
            st.bar_chart(df['content_rating'].value_counts())
            
            df['created_at'] = pd.to_datetime(df['created_at'])
            fig = px.scatter(df, x='created_at', y='likes', title='Creation time of Collected posts')
            st.plotly_chart(fig)
            
        else:
            st.error("No data found for the given user ID.")

if __name__ == "__main__":
    main()
