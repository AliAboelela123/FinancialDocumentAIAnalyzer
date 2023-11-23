"""
Flask Server Module to Handle Requests and Provide LLM Responses.
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from waitress import serve
from werkzeug.utils import secure_filename
import os

from LLMChain import get_response
from embeddings_db import get_best_chunks, store_embeddings
from utilities import allowed_file


# Flask app setup
app = Flask(__name__)
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'

# Setup CORS
CORS(app)

ALLOWED_EXTENSIONS = {'pdf'}

current_directory = os.path.dirname(os.path.abspath(__file__))
upload_directory = os.path.join(current_directory, 'uploads')
if not os.path.exists(upload_directory):
    os.makedirs(upload_directory)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/hello')
def hello():
    """
    Test endpoint to check if the server is responding.
    """
    return jsonify({"message": "Hello world!"})


@app.route('/query', methods=['POST'])
def query_endpoint():
    try:
        query = request.form.get('query')
        if not query:
            return jsonify({'error': "No Query Provided."}), 400
        complexity = request.form.get('complexity', 'Expert')
        pdf_files = []
        context = None

        print("Files Received:", request.files)

        # Check for PDF Files in the Request
        if 'pdfFiles' in request.files:
            files = request.files.getlist('pdfFiles')
            for file in files:
                print("Processing File:", file.filename)

                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_directory, filename)
                    file.save(file_path)
                    pdf_files.append(file_path)
                    # Assuming store_embeddings function returns context
                    store_embeddings(file_path)
                    # Debug print
                    print("File Saved:", file_path)
        
        context = get_best_chunks(query)
        llm_response = get_response(query, complexity, context)

        if llm_response:
            response_data = {'response': llm_response}
            if pdf_files:
                response_data['files'] = [os.path.basename(f) for f in pdf_files]
            return jsonify(response_data), 200
        else:
            return jsonify({'error': "No Response From the Language Model."}), 500
    except Exception as e:
        print(f"An Exception Occurred: {e}")
        return jsonify({'error': str(e)}), 500


def start_server():
    """
    Start the Flask server with waitress as the production server.
    """
    serve(app, host='0.0.0.0', port=5001)


if __name__ == '__main__':
    start_server()
