import os
import subprocess
import sys
import streamlit as st
import requests
import pandas as pd
from transformers import pipeline

# Function to run shell commands
def run_command(command):
    result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    return result.stdout.decode('utf-8'), result.stderr.decode('utf-8')

# Function to upgrade pip
def upgrade_pip():
    try:
        print("Upgrading pip...")
        stdout, stderr = run_command(f"{sys.executable} -m pip install --upgrade pip")
        print(stdout)
        if stderr:
            print(f"Error upgrading pip: {stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to upgrade pip: {e.stderr}")

# Function to install required Python packages from requirements.txt
def install_requirements():
    try:
        print("Installing Python dependencies from requirements.txt...")
        stdout, stderr = run_command(f"{sys.executable} -m pip install -r requirements.txt")
        print(stdout)
        if stderr:
            print(f"Error installing dependencies: {stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e.stderr}")

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

# Function to summarize text
def summarize_text(text):
    summarizer = pipeline("text2text-generation", model="JorgeSarry/est5-summarize")
    summary = summarizer(text, max_length=150, min_length=50, do_sample=False)
    return summary[0]['generated_text']

# Main function
if __name__ == "__main__":
    upgrade_pip()
    install_requirements()

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

    # Section for Text Summarizer
    st.subheader("Summarize Text")
    user_text = st.text_area("Enter text to summarize", height=200)

    if st.button("Summarize"):
        if user_text:
            with st.spinner('Summarizing text...'):
                summary = summarize_text(user_text)
                st.success("Summary:")
                st.write(summary)
        else:
            st.warning("Please enter text to summarize.")
