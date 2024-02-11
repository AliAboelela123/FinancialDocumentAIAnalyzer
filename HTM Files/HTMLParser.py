import json
import os
from bs4 import BeautifulSoup

def append_to_jsonl_file(data, jsonl_file_path):
    """
    Append data to a JSONL file. Creates the file if it does not exist.

    :param data: Dictionary containing the data to append.
    :param jsonl_file_path: Path to the JSONL file.
    """
    mode = 'a' if os.path.exists(jsonl_file_path) else 'w'
    with open(jsonl_file_path, mode, encoding='utf-8') as jsonl_file:
        jsonl_file.write(json.dumps(data) + '\n')

def process_html_file(file_path, output_jsonl_file):
    # Check if the HTML file exists
    if not os.path.exists(file_path):
        return "HTML File Not Found."

    with open(file_path, 'r', encoding='utf-8') as file:
        html_content = file.read()
    soup = BeautifulSoup(html_content, 'html.parser')

    paragraphs = [p.get_text(separator='\n', strip=True) for p in soup.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6'])]

    # Extract and format tables
    tables = []
    for table in soup.find_all('table'):
        rows = []
        for row in table.find_all('tr'):
            cells = [cell.get_text(strip=True) for cell in row.find_all(['th', 'td'])]
            rows.append(' | '.join(cells))
        tables.append('\n'.join(rows))

    # Combine paragraphs and tables
    combined_text = ' '.join(paragraphs + tables)

    # Create JSONL content
    jsonl_content = {
        "messages": [
            {"role": "system", "content": "You are a financial AI that is trained on the top 30 companies in the S&P500, specially their 10Q forms."},
            {"role": "user", "content": "For Apple, in 2023 Q4, what is its Quarterly Report?"},
            {"role": "assistant", "content": combined_text}
        ]
    }

    # Append to JSONL file
    append_to_jsonl_file(jsonl_content, output_jsonl_file)

    return f"Content Appended to {output_jsonl_file}"

# Define the path to the HTML file and the JSONL file
file_path = 'AMEX_HTML.html'
output_jsonl_file = 'Apple.jsonl'

# Process the HTML file and append to the JSONL file
result = process_html_file(file_path, output_jsonl_file)
print("Done")
