# FINAL llm.py

import os
from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import sqlparse
import re

# Load Environment
load_dotenv()
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
base_url = "http://localhost:11434"
model = "gemma3:4b"

llm = ChatOllama(base_url=base_url, model=model)

# --- SQL Schema RAG ---
ALLOWED_SCHEMA = {
    "Product": ["product_id", "product_name", "product_quantity", "category", "brand_name"],
    "Invoice": ["invoice_id", "invoice_date", "car_number", "invoice_status", "payment_method", "amount_paid", "discount"],
    "Employee": ["employee_id", "employee_name", "role", "hired_date", "notes"],
    "DailySales": ["daily_sales_id", "date", "total_sales_omzet", "salary_paid", "salary_status", "employee_id", "invoice_id"],
    "ItemInInvoice": ["invoice_detail_id", "discount_per_item", "quantity", "price", "invoice_id", "product_id"],
    "EmployeeAttendance": ["employee_absence_id", "date", "clock_in", "clock_out", "day_count", "absence_status", "notes", "employee_id"],
    "EmployeePayroll": ["employee_payroll_id", "payment_date", "sales_omzet_amount", "salary_amount", "employee_id"],
    "EmployeeBenefits": ["employee_bonus_id", "date", "bonus_type", "amount", "status", "notes", "employee_id"],
    "EkspedisiMasuk": ["ekspedisi_id", "date", "quantity", "purchase_price", "sale_price", "in_or_out", "product_id"],
    "Chatbot": ["chatbot_id", "user_id", "answer", "question", "timestamp"]
}

schema_context = "\n".join([f'Table "{table}": {", ".join(columns)}' for table, columns in ALLOWED_SCHEMA.items()])

# --- PROMPTING LLM ---
system_sql = SystemMessagePromptTemplate.from_template(f"""
You are a PostgreSQL query generator.
ONLY output one valid SQL SELECT query. NO explanations, NO markdown.

Use only these tables and columns:
{schema_context}

✅ Rules:
- Wrap identifiers in double quotes (").
- Table names: PascalCase.
- Columns: snake_case.
- Always fully close parentheses.
- When counting, use COUNT(*).
- Never hallucinate non-listed columns or tables.
- Return only pure PostgreSQL syntax.

🚨 Forbidden:
- <think> ... </think>
- ```sql
- Wrong table/column names
- Wrong parentheses
- Incomplete queries

If unsure, reply: "I'm not sure."
""")

human_sql = HumanMessagePromptTemplate.from_template("""
Write a pure SELECT query for PostgreSQL answering:
Question: {question}
""")

template_sql = ChatPromptTemplate.from_messages([system_sql, human_sql])
chain_sql = template_sql | llm | StrOutputParser()

# --- SQL SYNTAX CLEANER & VALIDATOR ---
def clean_sql_output(sql: str) -> str:
    sql = sql.strip()
    sql = sql.replace('`', '"').replace('‘', '"').replace('’', '"').replace('“', '"').replace('”', '"')
    sql = sql.replace("double_quote(", "").replace(")", "")
    sql = sql.replace('""', '"')
    if 'COUNT(*' in sql and 'COUNT(*)' not in sql:
        sql = sql.replace('COUNT(*', 'COUNT(*)')
    if 'COUNT(* FROM' in sql:
        sql = sql.replace('COUNT(* FROM', 'COUNT(*) FROM')
    return sql

def is_valid_sql(query):
    try:
        parsed = sqlparse.parse(query)
        return parsed is not None and len(parsed) > 0 and "SELECT" in query.upper()
    except Exception:
        return False

def ask_llm(question):
    raw_sql = chain_sql.invoke({"question": question})
    cleaned_sql = clean_sql_output(raw_sql)
    return cleaned_sql

# --- FINAL NATURAL LANGUAGE SUMMARIZER ---
system_summary = SystemMessagePromptTemplate.from_template("""
You are a polite AI assistant.
Reply in Indonesian if the question is Indonesian.
Otherwise, reply in English.
Summarize clearly and concisely.
""")
human_summary = HumanMessagePromptTemplate.from_template("""
Question: {question}
Result: {result}
""")

template_summary = ChatPromptTemplate.from_messages([system_summary, human_summary])
chain_summary = template_summary | llm | StrOutputParser()

def summarize_answer(question, result):
    return chain_summary.invoke({"question": question, "result": result})
