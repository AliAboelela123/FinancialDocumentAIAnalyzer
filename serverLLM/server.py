from flask import Flask, Response, jsonify, request, stream_with_context
from flask_cors import CORS
from waitress import serve
from werkzeug.utils import secure_filename
import os
import json
import openai

from LLMChain import get_response
from embeddings_db import get_best_chunks, store_text, store_tables
from utilities import allowed_file, extractCsv, find_references
from config import OPEN_AI_API_KEY

openai.api_key = OPEN_AI_API_KEY

#global variable for csv string
combinedTables = ''

# global variables holding most recent context & response of the LLM, used to compute references
final_response = ""
best_text_chunks = []
best_table_chunks = []

# Flask app setup
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Setup CORS for Handling Cross-Origin Requests
CORS(app)

# Define Allowed Extensions for File Uploads
ALLOWED_EXTENSIONS = {'pdf'}

# Set Up Upload Directory
current_directory = os.path.dirname(os.path.abspath(__file__))
upload_directory = os.path.join(current_directory, 'uploads')
if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)

# Endpoint for Processing Queries
@app.route('/query', methods=['POST'])
def query_endpoint():
    """Handle Query Requests and Provide LLM Responses."""
    global final_response
    global best_text_chunks
    global best_table_chunks

    final_response = ""

    try:
        query = request.form.get('query')
        complexity = request.form.get('complexity', 'Expert')
        if not query:
            return jsonify({'error': "No Query Provided."}), 400

        complexity = request.form.get('complexity', 'Expert')
        pdf_files = []

        print("Files Received:", request.files)
        # Check for PDF Files in the Request
        if 'pdfFiles' in request.files:
            files = request.files.getlist('pdfFiles')
            for file in files:
                print("Processing File:", file.filename)
                # Process the File
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_directory, filename)
                    file.save(file_path)
                    pdf_files.append(file_path)
                    numFiles = extractCsv(file_path)
                    store_tables("./", numFiles, filename)
                    store_text(file_path, filename)
                    # Debug Print
                    print("File Saved:", file_path)

        best_text_chunks, best_table_chunks = get_best_chunks(query)

        def generate_responses():
            """Stream Responses to the Client."""
            global final_response
            try:
                for response_part in get_response(query, complexity, best_text_chunks, best_table_chunks):
                    # Check if the Response Part Is an Error
                    if isinstance(response_part, dict) and response_part.get('error'):
                        yield f"data: {json.dumps({'data': response_part})}\n\n"
                        break
                    else:
                        final_response += response_part
                        yield json.dumps({'data': response_part}) + '\n\n'
            except Exception as e:
                # Yield an Error Message if an Exception Occurs
                yield json.dumps({'error': str(e)}) + '\n\n'

        return Response(stream_with_context(generate_responses()), mimetype='application/json'), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/references', methods=['GET'])
def query_references():
    print("In References Endpoint")

    references = find_references(best_text_chunks, final_response)

    if not references:
        return jsonify({'error': "No References Available"})

    print(references)
    return jsonify({'references': references})

@app.route('/extractedTable', methods=['GET'])
def sendTable():
    print("In Extracted Endpoint")

    if not best_table_chunks[0].text:
        return jsonify({'error': "No Tables Available"})
    prompt = "Please format to CSV and clean up the following table data:\n" + "\n\n".join(best_table_chunks[0].text)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a friendly chatbot having a conversation with a human."},
                {"role": "user", "content": prompt}
            ],
            temperature=0
        )
        formatted_tables = response.choices[0].message['content']
        print("The formatted table after passing to GPT are: ",formatted_tables)
        return jsonify({'formattedTables': formatted_tables})
    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({'error': "Failed to format table."})


# Start the Server
def start_server():
    """Start the Flask Server with Waitress as the Production Server."""
    serve(app, host='0.0.0.0', port=5001)

# Main Entry Point
if __name__ == '__main__':
    start_server()
