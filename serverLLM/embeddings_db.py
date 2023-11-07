import os
import pandas as pd
import matplotlib.pyplot as plt
from transformers import GPT2TokenizerFast
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain.llms import OpenAI
from langchain.chains import ConversationalRetrievalChain
from flask import jsonify
from serverLLM.config import OPEN_AI_API_KEY

os.environ["OPENAI_API_KEY"] = OPEN_AI_API_KEY

db = None

def store_embeddings(file_path):
    global db

    if file_path is None:
        return None

    # Load the PDF and split it into pages
    loader = PyPDFLoader(file_path)
    pages = loader.load_and_split()
    chunks = pages
        
    # Get embedding model
    embeddings = OpenAIEmbeddings()

    # Create vector database
    db = FAISS.from_documents(chunks, embeddings)

    # The embeddings are now stored, and we can return a success status or any identifier required
    return True


def get_best_chunks(query):
    global db
    if db is None:
        return None
    # Perform a similarity search with the given query
    docs = db.similarity_search(query)
    return docs

    