import json
from pathlib import Path
from dotenv import load_dotenv
import os

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

# Load environment variables and verify API key
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your .env")

# 1) Read the entire JSON export
base_path = Path(__file__).parent
json_path = base_path / "data_export.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2) Convert JSON data to a single Document
#    (you could split per key if desired)
raw_content = json.dumps(data, indent=2)
docs = [Document(page_content=raw_content, metadata={"source": str(json_path)})]

# 3) Split into manageable text chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
texts = splitter.split_documents(docs)

# 4) Embed & persist vector store
emb = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
db_dir = base_path / "db"
vectorstore = Chroma.from_documents(texts, emb, persist_directory=str(db_dir))
vectorstore.persist()

print("✅ index rebuilt at", db_dir)
