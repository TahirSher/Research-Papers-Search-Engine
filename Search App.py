import os
import subprocess
import sys
import streamlit as st
import requests
import pandas as pd

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

# Function to install system dependencies (Linux)
def install_system_dependencies():
    try:
        print("Installing system dependencies...")
        # For Debian/Ubuntu
        command = "sudo apt-get update && sudo apt-get install -y python3-dev libjpeg-dev zlib1g-dev"
        stdout, stderr = run_command(command)
        print(stdout)
        if stderr:
            print(f"Error installing system dependencies: {stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install system dependencies: {e.stderr}")

# Function to install required Python packages
def install_requirements():
    try:
        print("Installing Python dependencies...")
        # Specify your requirements here
        requirements = "streamlit requests pandas Pillow==9.5.0"
        stdout, stderr = run_command(f"{sys.executable} -m pip install {requirements}")
        print(stdout)
        if stderr:
            print(f"Error installing dependencies: {stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install dependencies: {e.stderr}")

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

# Main function
if __name__ == "__main__":
    upgrade_pip()
    
    # Uncomment the next line if running on a local Linux machine
    # install_system_dependencies()
    
    install_requirements()

    # Start Streamlit App
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
