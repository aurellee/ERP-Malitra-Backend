# # malitra_service/utils/update_vectorstore_from_postgres.py

# import json
# from pathlib import Path
# from langchain.schema import Document
# from langchain_text_splitters import RecursiveCharacterTextSplitter
# from langchain_openai import OpenAIEmbeddings
# from langchain_chroma import Chroma
# from sqlalchemy import create_engine, text
# from dotenv import load_dotenv
# import os
# import shutil

# # Load environment
# load_dotenv()

# # Configuration
# POSTGRES_URI = os.getenv("POSTGRES_URI")  # Example: "postgresql+psycopg2://user:pass@localhost:5432/dbname"
# CHROMA_PATH = "chroma_db"

# # try:
# #     engine = create_engine(POSTGRES_URI)
# #     with engine.connect() as conn:
# #         result = conn.execute(text("SELECT 1"))
# #         print("✅ Connected Successfully!")
# # except Exception as e:
# #     print(f"❌ Failed to connect: {e}")


# def update_vectorstore_from_db():
#     engine = create_engine(POSTGRES_URI)
#     documents = []

#     with engine.connect() as conn:
#         print("🔵 Connected to PostgreSQL.")

#         # Fetch and build documents per table
#         TABLE_QUERIES = {
#             "products": 'SELECT * FROM "Product"',
#             "users": 'SELECT * FROM "User"',
#             "employees": 'SELECT * FROM "Employee"',
#             "ekspedisi": 'SELECT * FROM "EkspedisiMasuk"',
#             "invoices": 'SELECT * FROM "Invoice"',
#             "daily_sales": 'SELECT * FROM "DailySales"',
#             "employee_benefits": 'SELECT * FROM "EmployeeBenefits"',
#             "attendance": 'SELECT * FROM "EmployeeAttendance"',
#             "payroll": 'SELECT * FROM "EmployeePayroll"',
#             "chatbot": 'SELECT * FROM "Chatbot"',
#             "item_in_invoice": 'SELECT * FROM "ItemInInvoice"',
#         }

#         for table_name, query in TABLE_QUERIES.items():
#             try:
#                 result = conn.execute(text(query))
#                 rows = result.fetchall()
#                 print(f"✅ {len(rows)} rows fetched from {table_name}.")
#                 ...
#             except Exception as e:
#                 print(f"⚠️ Failed to fetch {table_name}: {e}")

#             for row in rows:
#                 # Turn each row into a document
#                 content = "\n".join(f"{key}: {value}" for key, value in row._mapping.items())
#                 documents.append(Document(page_content=content, metadata={"table": table_name}))

#     print(f"📚 Total {len(documents)} documents ready to embed.")

#     # Split text
#     splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
#     chunks = splitter.split_documents(documents)

#     # Clean previous vectorstore
#     db_path = Path(CHROMA_PATH)
#     if db_path.exists():
#         shutil.rmtree(db_path)
#         print(f"🧹 Old chroma_db cleared.")

#     # Initialize embeddings
#     embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

#     # Build new vectorstore
#     vectorstore = Chroma(
#         collection_name="erp_malitra_collection",
#         embedding_function=embedding_model,
#         persist_directory=CHROMA_PATH,
#     )
#     vectorstore.add_documents(chunks)

#     print(f"✅ Vectorstore rebuilt and saved at {CHROMA_PATH}. Total chunks: {len(chunks)}")


# if __name__ == "__main__":
#     update_vectorstore_from_db()

#     # Fetch data
#     # with engine.connect() as conn:
#     #     result = conn.execute(text("SELECT * FROM employee_attendance"))
#     #     rows = result.fetchall()

#     # print(f"✅ Fetched {len(rows)} rows from database.")

#     # # Transform to Documents
#     # documents = []
#     # for row in rows:
#     #     content = f"""
#     #     Employee ID: {row['employee_id']}
#     #     Attendance Date: {row['date']}
#     #     Clock In: {row['clock_in']}
#     #     Clock Out: {row['clock_out']}
#     #     Status: {row['absence_status']}
#     #     Notes: {row['notes']}
#     #     """
#     #     documents.append(Document(page_content=content, metadata={"source": "attendance"}))

#     # # Split Documents
#     # splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=100)
#     # chunks = splitter.split_documents(documents)

#     # print(f"✅ Split into {len(chunks)} chunks.")

#     # # Initialize Embeddings
#     # embedding_model = OpenAIEmbeddings(model="text-embedding-3-large")

#     # # Clean existing DB
#     # db_path = Path(CHROMA_PATH)
#     # if db_path.exists():
#     #     shutil.rmtree(db_path)
#     #     print(f"🧹 Cleaned existing Chroma database at {CHROMA_PATH}.")

#     # # Rebuild vectorstore
#     # vectorstore = Chroma(
#     #     collection_name="erp_malitra_collection",
#     #     embedding_function=embedding_model,
#     #     persist_directory=CHROMA_PATH,
#     # )

#     # vectorstore.add_documents(chunks)
#     # vectorstore.persist()

#     # print(f"✅ Rebuilt and saved new Chroma vectorstore at {CHROMA_PATH}.")