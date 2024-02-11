import pandas as pd
from pymongo import MongoClient
import os
import requests
import re
from bs4 import BeautifulSoup
import time

# Load CIK Numbers from CSV
cik_df = pd.read_excel('CLK_NUMBERS.xlsx', header=None, dtype={0: str})
# cik_numbers = cik_df[0].tolist()
cik_numbers = ['0000004962']
print(f"CIK Numbers: {cik_numbers[:5]}")  # Print first 5 CIK numbers

# MongoDB Setup
client = MongoClient('localhost', 9999)
db = client.edgar_reports
collection = db.quarterly_reports
base_dir = "/Users/nelsonlee/Documents/Winter 2024/ECE496/FinancialDocumentAIAnalyzer/Quarterly Reports Test 3"

headers = {
    'User-Agent': 'Mozilla/5.0'
}


def get_10q_links(cik):
    base_url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={cik}&type=10-Q&dateb=&owner=exclude&count=10"
    page = requests.get(base_url, headers=headers)
    print(page.status_code)
    if page.status_code != 200:
        print(f"Failed to fetch {base_url}")
        return []
    soup = BeautifulSoup(page.content, 'html.parser')
    table = soup.find('table', class_='tableFile2')
    if not table:
        print(f"No table found for CIK: {cik}")
        return []
    
    links = []
    for row in table.find_all('tr')[1:]:
        cols = row.find_all('td')
        if len(cols) > 3:
            link = cols[1].find('a')
            if link:
                links.append("https://www.sec.gov" + link['href'])
    print(f"Found {len(links)} links for CIK: {cik}")
    return links


# Iterate over CIK numbers and fetch links
all_links = {}
for cik in cik_numbers:
    all_links[cik] = get_10q_links(cik)

def parse_and_save_tables(url, cik):
    try:
        print(f"Accessing filing page for CIK: {cik}")
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all tables
        tables = soup.find_all('table')
        for i, table in enumerate(tables, start=1):
            # Extract table headers
            headers = [header.get_text(strip=True) for header in table.find_all('th')]

            # Extract table rows
            rows = []
            for row in table.find_all('tr'):
                rows.append([cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])])

            # Convert to DataFrame
            df = pd.DataFrame(rows, columns=headers)

            # Define the directory and file path
            cik_dir = os.path.join('Documents/Winter 2024/ECE496/FinancialDocumentAIAnalyzer', cik)
            os.makedirs(cik_dir, exist_ok=True)
            file_name = f"{cik}_table_{i}.csv"
            file_path = os.path.join(cik_dir, file_name)
            
            # Save the table to CSV
            df.to_csv(file_path, index=False)
            print(f"Table {i} saved to {file_path}")
    
    except Exception as e:
        print(f"An error occurred: {e}")


def download_report(url, cik):
    try:
        print(f"Accessing filing page for CIK: {cik}")
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find the first .htm link (assuming the first .htm is the report)
        link = soup.find('a', text=lambda x: x and x.endswith('.txt'))
        if link:
            htm_link = "https://www.sec.gov" + link['href']
            print(f"Downloading report from {htm_link}")
            htm_response = requests.get(htm_link)
            htm_soup = BeautifulSoup(htm_response.content, 'html.parser')

            # Extract text using BeautifulSoup
            report_text = htm_soup.get_text(separator='\n', strip=True)

            # Additional cleaning to remove HTML entities and unwanted patterns
            cleaned_text = re.sub(r'\s+', ' ', report_text)  # Replace multiple spaces with a single space
            cleaned_text = re.sub(r'&[a-zA-Z]+;', '', cleaned_text)  # Remove HTML entities

            # Create directory for CIK if it doesn't exist
            cik_dir = os.path.join(base_dir, cik)
            os.makedirs(cik_dir, exist_ok=True)

            # Define file name and path
            file_name = f"{cik}_{htm_link.split('/')[-1].replace('.htm', '.txt')}"
            file_path = os.path.join(cik_dir, file_name)

            # Write the cleaned text to a file
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(cleaned_text)
            print(f"Report saved to {file_path}")
        else:
            print("No .htm file found for this report.")
    except Exception as e:
        print(f"An error occurred: {e}")


# Download Reports
REQUESTS_PER_SECOND = 9
REQUEST_INTERVAL = 1.0 / REQUESTS_PER_SECOND


def process_cik(cik):
    start_time = time.time()
    links = get_10q_links(cik)
    for link in links:
        download_report(link, cik)
        parse_and_save_tables(link, cik)
        time.sleep(max(0, REQUEST_INTERVAL - (time.time() - start_time)))
        start_time = time.time()


# Iterate over CIK numbers and process each
for cik in cik_numbers:
    print(f"Processing CIK: {cik}")
    process_cik(cik)