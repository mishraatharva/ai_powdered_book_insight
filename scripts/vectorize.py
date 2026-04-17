import glob
import pandas as pd

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS

from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_experimental.text_splitter import SemanticChunker

from langchain_groq import ChatGroq
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from dotenv import load_dotenv
from langchain_mistralai import MistralAIEmbeddings
from langchain_ollama import OllamaEmbeddings
import os

# -------------------------------
#  STEP 1: CREATE VECTOR DB
# -------------------------------


def get_embeddings():
    return OllamaEmbeddings(model="nomic-embed-text")



def create_vector_db(data_dir):
    documents = []
    
    data_dir = data_dir or "U:\assignment\ai_powdered_book_insight\scraper\data\with_description"

    csv_files = glob.glob(os.path.join(data_dir, "*.csv"))

    for file in csv_files:
        df = pd.read_csv(file)
        genre = os.path.basename(file).replace("_books.csv", "")

        for _, row in df.iterrows():

            description = str(row.get("description", ""))

            if not description or description == "nan":
                continue

            # Hybrid content (metadata + description)
            content = f"""
            Title: {row.get('title', '')}
            Author: {row.get('author', '')}
            Rating: {row.get('rating', '')}
            Reviews: {row.get('reviews', '')}

            Description:
            {description}
            """

            metadata = {
                "title": row.get("title", ""),
                "author": row.get("author", ""),
                "rating": row.get("rating", ""),
                "reviews": row.get("reviews", ""),
                "url": row.get("url", ""),
                "genre": genre,
                "source_file": os.path.basename(file)
            }

            documents.append(Document(
                page_content=content.strip(),
                metadata=metadata
            ))
    
    print(f" Loaded {len(documents)} documents")
    
    embeddings = get_embeddings()
    
    # -------------------------------
    #  SEMANTIC CHUNKING
    # -------------------------------
    semantic_splitter = SemanticChunker(
        embeddings,
        breakpoint_threshold_type="percentile"
    )
    
    semantic_docs = semantic_splitter.split_documents(documents)
    print(f" Semantic chunks: {len(semantic_docs)}")
    
    # -------------------------------
    # OVERLAP CHUNKING
    # -------------------------------
    overlap_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=100
    )
    
    final_docs = overlap_splitter.split_documents(semantic_docs)
    print(f" Final chunks: {len(final_docs)}")
    
    # -------------------------------
    # VECTOR STORE
    # -------------------------------
    vectorstore = FAISS.from_documents(final_docs, embeddings)
    
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    save_path = os.path.join(BASE_DIR, "vector_store", "faiss_books_index")
    os.makedirs(save_path, exist_ok=True)
    vectorstore.save_local(save_path)
    
    vectorstore.save_local(r"U:\assignment\ai_powdered_book_insight\vector_store\faiss_books_index")

    print("Vector DB created and saved!")


if __name__ == "__main__":
    load_dotenv()  # Load environment variables from .env file
    create_vector_db(r"U:\assignment\ai_powdered_book_insight\scraper\data\with_description")