import os
import uuid
import PyPDF2 
import openai
from config import OPEN_AI_API_KEY
from sklearn.metrics.pairwise import cosine_similarity
import fitz

os.environ["OPENAI_API_KEY"] = OPEN_AI_API_KEY

vector_index = []
text_index = {}

def get_embedding(chunk):
    # Ensure that the chunk is a string and not empty
    if not isinstance(chunk, str) or not chunk.strip():
        raise ValueError("Chunk Must Be a Non-Empty String")

    try:
        # OpenAI's API expects a list of texts
        openai.api_key = OPEN_AI_API_KEY
        response = openai.Embedding.create(
            input=[chunk],
            model="text-embedding-ada-002"
        )
        # Extract embedding from the response
        embedding = response['data'][0]['embedding']
        return embedding
    except openai.error.InvalidRequestError as e:
        print("Invalid Request to OpenAI API:", e)
        raise
    except Exception as e:
        print("An Exception Occurred While Getting Embeddings:", e)
        raise


def pdf_to_text(file_path):
    text_list = []
    with fitz.open(file_path) as doc:
        for page in doc:
            text_list.append(page.get_text())
    return text_list


def store_embeddings(file_path):
    if file_path is None:
        return False

    # Load the PDF and split it into pages
    string_chunks = pdf_to_text(file_path)
    # Get embedding model
    for chunk in string_chunks:
        if not chunk.strip():
            print("Skipping Empty Chunk")
            continue

        try:
            random_uuid = str(uuid.uuid4())
            text_index[random_uuid] = chunk
            chunk_embedding = get_embedding(chunk)
            vector_index.append((random_uuid, chunk_embedding))
        except ValueError as e:
            print(f"Skipping Chunk Due to Error: {e}")
        except Exception as e:
            print(f"An Exception Occurred While Processing Chunk: {e}")

    return True


def get_best_chunks(query):
    if not vector_index:
        return "No Documents Have been Uploaded or Processed for Similarity."

    query_vector = get_embedding(query)
    embedding_vector = [embedding for _, embedding in vector_index]

    if not isinstance(embedding_vector, list) or not embedding_vector:
        return "No Embeddings Found for the Documents."

    try:
        cosine_sim = cosine_similarity([query_vector], embedding_vector)
        max_index = cosine_sim.argmax()
        best_uuid = vector_index[max_index][0]
        best_text = text_index[best_uuid]
        return best_text
    except ValueError as e:
        print(f"An Exception Occurred While Computing Cosine Similarity: {e}")
        return "An Error Occurred While Processing the Documents."
