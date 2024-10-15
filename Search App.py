import streamlit as st
import requests
import pandas as pd

# Function to search CrossRef using the user's query
def search_crossref(query, rows=10):
    # CrossRef API endpoint
    url = "https://api.crossref.org/works"
    
    # Parameters for the API request
    params = {
        "query": query,  # The search query from the user
        "rows": rows,    # Number of results to return
        "filter": "type:journal-article"  # Filter for journal articles only
    }
    
    try:
        # Send the GET request to CrossRef API
        response = requests.get(url, params=params)
        response.raise_for_status()  # Raise an error for bad responses
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
        
        # Convert list of papers to a Pandas DataFrame for easy display
        df = pd.DataFrame(paper_list)
        st.write(df)
    else:
        st.warning("No data to display.")

# Streamlit App
st.title("Research Paper Finder")

# Input field for user's query
query = st.text_input("Enter your research topic or keywords", value="machine learning optimization")

# Number of papers to retrieve
num_papers = st.slider("Select number of papers to retrieve", min_value=5, max_value=50, value=10)

# Search button
if st.button("Search"):
    # Fetch and display results
    if query:
        with st.spinner('Searching for papers...'):
            response_data = search_crossref(query, rows=num_papers)
            display_results(response_data)
    else:
        st.warning("Please enter a search query.")
