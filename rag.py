import os
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

load_dotenv()
# -------------------------------
#  STEP 1: CREATE VECTOR DB
# -------------------------------

def get_embeddings():
    return OllamaEmbeddings(model="nomic-embed-text")



def create_vector_db(data_dir="U:/assignment/ai_powdered_book_insight/with_description"):
    documents = []
    
    data_dir = data_dir or "U:/assignment/ai_powdered_book_insight/with_description"

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
    vectorstore.save_local("faiss_books_index")

    print("Vector DB created and saved!")

    return vectorstore


# -------------------------------
#  LOAD VECTOR DB
# -------------------------------
def load_vector_db():
    return FAISS.load_local("faiss_books_index", get_embeddings())


# -------------------------------
#  QUERY REWRITER (BONUS++)
# -------------------------------
def rewrite_query(query, llm):
    prompt = f"""
    Rewrite the user query to be more specific and optimized for semantic search.

    User Query: {query}

    Improved Query:
    """
    return llm.invoke(prompt).strip()


# -------------------------------
# CREATE QA CHAIN
# -------------------------------
def get_qa_chain(vectorstore):
    retriever = vectorstore.as_retriever(
        search_type="mmr",  #  better than similarity
        search_kwargs={"k": 5, "fetch_k": 10}
    )

    llm = ChatGroq(
        temperature=0,
        model="gpt-4o-mini"
    )

    return retriever, llm


# -------------------------------
#  ASK FUNCTION (RAG FLOW)
# -------------------------------
def ask_question(query, retriever, llm):
    #  Step 1: Rewrite query
    improved_query = rewrite_query(query, llm)

    # Step 2: Retrieve documents
    docs = retriever.get_relevant_documents(improved_query)

    #  Step 3: Build context
    context = "\n\n".join([doc.page_content for doc in docs])

    # Step 4: Final prompt
    prompt = f"""
    Answer the question using ONLY the context below.
    If answer not found, say "I don't know".

    Context:
    {context}

    Question:
    {query}

    Answer:
    """

    answer = llm.predict(prompt)

    # Step 5: Source citations
    sources = []
    for doc in docs:
        sources.append({
            "title": doc.metadata.get("title"),
            "url": doc.metadata.get("url")
        })

    return answer, sources


# -------------------------------
# MAIN
# -------------------------------
if __name__ == "__main__":
    # First time:
    vectorstore = create_vector_db()

    # Later:
    # vectorstore = load_vector_db()

    retriever, llm = get_qa_chain(vectorstore)

    while True:
        query = input("\n Ask a question: ")

        answer, sources = ask_question(query, retriever, llm)

        print("\n Answer:")
        print(answer)

        print("\n Sources:")
        for s in sources:
            print(f"{s['title']} → {s['url']}")