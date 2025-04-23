import json
from pathlib import Path
from dotenv import load_dotenv
import os

from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OpenAIEmbeddings

# Load environment variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Set OPENAI_API_KEY in your .env")

# 1) Read JSON export
base_path = Path(__file__).parent
json_path = base_path / "data_export.json"
with open(json_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# 2) Create Documents per top-level section
docs = []
for section, items in data.items():
    # Dump only this section's content
    content = json.dumps(items, indent=2)
    docs.append(Document(page_content=content, metadata={"section": section}))

# 3) Split into manageable chunks
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
texts = []
for doc in docs:
    # Each doc may produce multiple chunks
    texts.extend(splitter.split_documents([doc]))

# 4) Embed & persist vector store
emb = OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY)
db_dir = base_path / "db"
vectorstore = Chroma.from_documents(texts, emb, persist_directory=str(db_dir))
vectorstore.persist()  # ensure index is written to disk

print("✅ index rebuilt and persisted at", db_dir)