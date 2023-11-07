"""
Flask Server Module to Handle Requests and Provide LLM Responses.
"""

from flask import Flask, jsonify, request, session
from flask_cors import CORS
from waitress import serve
from werkzeug.utils import secure_filename
import os

from serverLLM.LLMChain import get_response
from serverLLM.embeddings_db import get_best_chunks, store_embeddings,db
from serverLLM.utilities import allowed_file


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
    """
    Endpoint to receive queries and provide LLM responses.
    """
    try:
        if 'query' not in request.form:
            return jsonify({'error': "No query provided."}), 400

        query = request.form['query']
        complexity_level = request.form.get('complexity', 'Expert')
        complexity = session.get('complexity', complexity_level)

        pdf_files = []

        # File Processing
        if 'pdfFiles' in request.files:
            files = request.files.getlist('pdfFiles')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_directory, filename)
                    file.save(file_path)
                    pdf_files.append(file_path)
                    store_embeddings(file_path)
                    print("File uploaded and processed successfully.")

        context = get_best_chunks(query)
        llm_response = get_response(query, complexity, context)

        print(f"Received LLM Response: {llm_response}")  # Log the LLM Response

        if llm_response:
            return jsonify({'response': llm_response, 'files': pdf_files}), 200
        else:
            print("No Response from LLMChain.")
            return jsonify({'error': "No Response from the Language Model."}), 500
    except Exception as e:
        print(f"An exception occurred: {e}")
        return jsonify({'error': str(e)}), 400


def start_server():
    """
    Start the Flask server with waitress as the production server.
    """
    serve(app, host='127.0.0.1', port=5000)


if __name__ == '__main__':
    start_server()
