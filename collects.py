import streamlit as st
import requests
import json
import pandas as pd
import plotly.express as px

def fetch_data(user_id, offset=0, limit=500):
    url = f"https://api.yodayo.com/v1/users/{user_id}/notes?offset={offset}&limit={limit}&width=100&include_nsfw=true"
    response = requests.get(url)
    return response.json()

def analyze_data(data):
    posts = data.get('posts', [])
    
    total_posts = len(posts)
    total_likes = sum(post['likes'] for post in posts)
    total_comments = sum(post['comments'] for post in posts)
    total_collects = sum(post['collects'] for post in posts)
    
    df = pd.DataFrame(posts)
    
    return {
        'total_posts': total_posts,
        'total_likes': total_likes,
        'total_comments': total_comments,
        'total_collects': total_collects,
        'df': df
    }

def main():
    st.title("Yodayo User Data Analyzer")
    
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
            st.success(f"Data fetched successfully. Total posts: {len(all_data)}")
            
            combined_data = {'posts': all_data}
            analysis = analyze_data(combined_data)
            
            st.header("Basic Statistics")
            st.write(f"Total Posts: {analysis['total_posts']}")
            st.write(f"Total Likes: {analysis['total_likes']}")
            st.write(f"Total Comments: {analysis['total_comments']}")
            st.write(f"Total Collects: {analysis['total_collects']}")
            
            st.header("Post Analysis")
            df = analysis['df']
            
            fig = px.histogram(df, x='likes', title='Distribution of Likes')
            st.plotly_chart(fig)
            
            st.subheader("Top 10 Most Liked Posts")
            st.dataframe(df.nlargest(10, 'likes')[['title', 'likes', 'comments', 'collects']])
            
            st.subheader("Content Rating Distribution")
            st.bar_chart(df['content_rating'].value_counts())
            
            df['created_at'] = pd.to_datetime(df['created_at'])
            fig = px.scatter(df, x='created_at', y='likes', title='Posts Timeline')
            st.plotly_chart(fig)
            
        else:
            st.error("No data found for the given user ID.")

if __name__ == "__main__":
    main()
