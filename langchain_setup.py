from pathlib import Path
from dotenv import load_dotenv
import os
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAIEmbeddings  # Updated import
from langchain.text_splitter import RecursiveCharacterTextSplitter
import openai

# Load environment variables from .env file
load_dotenv()

# Get OpenAI API Key from environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Ensure the API key is available
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found. Please set it in your .env file.")

# Set OpenAI API key to use for embeddings
openai.api_key = OPENAI_API_KEY

# Load and split documents
loader = TextLoader("data_export.txt")
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = splitter.split_documents(documents)

# Create embeddings using OpenAI
embedding = OpenAIEmbeddings()

# Create and persist the vector store
vectorstore = Chroma.from_documents(texts, embedding, persist_directory="./db")
vectorstore.persist()

print("Documents have been successfully processed and stored!")
