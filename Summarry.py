import streamlit as st
import requests
import pandas as pd
from transformers import pipeline
import tensorflow
import torch

# Function to search CrossRef using the user's query
def search_crossref(query, rows=10):
    url = "https://api.crossref.org/works"
    
    params = {
        "query": query,
        "rows": rows,
        "filter": "type:journal-article"
    }
    
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        st.error(f"HTTP error occurred: {e}")
        return None
    except Exception as e:
        st.error(f"An error occurred: {e}")
        return None

# Function to display the results in a table format
def display_results(data):
    if data:
        items = data.get('message', {}).get('items', [])
        if not items:
            st.warning("No results found for the query.")
            return
        
        paper_list = []
        for item in items:
            paper = {
                "Title": item.get('title', [''])[0],
                "Author(s)": ', '.join([author['family'] for author in item.get('author', [])]),
                "Journal": item.get('container-title', [''])[0],
                "DOI": item.get('DOI', ''),
                "Link": item.get('URL', ''),
                "Published": item.get('issued', {}).get('date-parts', [[None]])[0][0] if 'issued' in item else "N/A"
            }
            paper_list.append(paper)
        
        df = pd.DataFrame(paper_list)
        st.write(df)
    else:
        st.warning("No data to display.")

# Main function
if __name__ == "__main__":
    # Start Streamlit App
    st.title("Research Paper Finder and Text Summarizer")

    # Section for Research Paper Finder
    st.subheader("Find Research Papers")
    query = st.text_input("Enter your research topic or keywords", value="machine learning optimization")
    num_papers = st.slider("Select number of papers to retrieve", min_value=5, max_value=50, value=10)

    if st.button("Search"):
        if query:
            with st.spinner('Searching for papers...'):
                response_data = search_crossref(query, rows=num_papers)
                display_results(response_data)
        else:
            st.warning("Please enter a search query.")
