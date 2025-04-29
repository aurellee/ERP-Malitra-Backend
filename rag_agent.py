# ollama_chatbot.py

import os
from dotenv import load_dotenv
import sqlparse
from langchain_ollama import ChatOllama
from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import chain, RunnablePassthrough
from langchain_community.utilities import SQLDatabase

# Load Environment
load_dotenv()
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# Connect to DB
db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5432/erpmalitra")

# Setup LLM
llm = ChatOllama(base_url="http://localhost:11434", model="gemma3:4b")

# --- PROMPT for LLM SQL GENERATION ---
system_sql = SystemMessagePromptTemplate.from_template("""
You are a PostgreSQL SQL generator.

✅ RULES:
- Only generate VALID single SELECT PostgreSQL query.
- Table names: PascalCase. Column names: snake_case.
- Wrap ALL table and column names with double quotes (").
- Only allowed tables and columns are provided.
- NO explanations, NO markdown, NO comments, just pure SQL.
- No thinking step. Only final clean POSTGRESQL SQL.
- If unsure, respond: "I'm not sure."

✅ TABLES and COLUMNS:
Table "Chatbot": "chatbot_id", "user_id", "answer", "question", "timestamp"
Table "Product": "product_id", "product_name", "product_quantity", "category", "brand_name"
Table "Invoice": "invoice_id", "invoice_date", "car_number", "invoice_status", "payment_method", "amount_paid", "discount"
Table "DailySales": "daily_sales_id", "date", "total_sales_omzet", "salary_paid", "salary_status", "employee_id", "invoice_id"
Table "Employee": "employee_id", "employee_name", "role", "hired_date", "notes"
Table "EkspedisiMasuk": "ekspedisi_id", "date", "quantity", "purchase_price", "sale_price", "in_or_out", "product_id"
Table "ItemInInvoice": "invoice_detail_id", "discount_per_item", "quantity", "price", "invoice_id", "product_id"
Table "EmployeePayroll": "employee_payroll_id", "payment_date", "sales_omzet_amount", "salary_amount", "employee_id"
Table "EmployeeAttendance": "employee_absence_id", "date", "clock_in", "clock_out", "day_count", "absence_status", "notes", "employee_id"
Table "EmployeeBenefits": "employee_bonus_id", "date", "bonus_type", "amount", "status", "notes", "employee_id"

✅ Behavior:
- Count product stock ➔ COUNT(*) from "Product".
- Total sales omzet ➔ SUM("amount_paid") from "Invoice".
- Omzet karyawan ➔ SUM("amount_paid") WHERE sales or mechanic match.
- Absensi ➔ "EmployeeAttendance".
""")

human_sql = HumanMessagePromptTemplate.from_template("""
Write the POSTGRESQL to answer:

{question}
""")

template_sql = ChatPromptTemplate.from_messages([system_sql, human_sql])
chain_sql = template_sql | llm | StrOutputParser()

# --- SQL Syntax Checker ---
def is_valid_sql(query):
    try:
        parsed = sqlparse.parse(query)
        return parsed is not None and len(parsed) > 0
    except Exception:
        return False

# --- PREDEFINED QUERY MAPPER ---
def predefined_query(question):
    q = question.lower()

    if "total produk" in q or "jumlah produk" in q:
        return 'SELECT COUNT(*) FROM "Product";'
    if "total invoice" in q or "jumlah invoice" in q:
        return 'SELECT COUNT(*) FROM "Invoice";'
    if "total omzet" in q and "sales" not in q:
        return 'SELECT SUM("amount_paid") FROM "Invoice";'
    if "total omzet sales ryan prakoso" in q:
        return 'SELECT SUM("amount_paid") FROM "Invoice" WHERE "sales" = \'Ryan Prakoso\' OR "mechanic" = \'Ryan Prakoso\';'
    if "jumlah employee" in q or "total employee" in q:
        return 'SELECT COUNT(*) FROM "Employee";'
    if "total bonus karyawan" in q:
        return 'SELECT SUM("amount") FROM "EmployeeBenefits" WHERE EXTRACT(YEAR FROM "date") = EXTRACT(YEAR FROM CURRENT_DATE);'
    if "total absensi hari ini" in q:
        return 'SELECT COUNT(*) FROM "EmployeeAttendance" WHERE "date" = CURRENT_DATE;'
    if "total omzet dailysales bulan ini" in q:
        return 'SELECT SUM("total_sales_omzet") FROM "DailySales" WHERE EXTRACT(MONTH FROM "date") = EXTRACT(MONTH FROM CURRENT_DATE);'
    if "jumlah invoice lunas" in q or "invoice sudah lunas" in q:
        return 'SELECT COUNT(*) FROM "Invoice" WHERE "invoice_status" = \'Paid\';'
    if "produk keluar" in q:
        return 'SELECT SUM("quantity") FROM "EkspedisiMasuk" WHERE "in_or_out" = \'OUT\';'
    if "produk masuk" in q:
        return 'SELECT SUM("quantity") FROM "EkspedisiMasuk" WHERE "in_or_out" = \'IN\';'
    if "gaji dibayarkan" in q or "total gaji" in q:
        return 'SELECT SUM("salary_amount") FROM "EmployeePayroll";'
    if "sales omzet payroll" in q:
        return 'SELECT SUM("sales_omzet_amount") FROM "EmployeePayroll";'
    if "item invoice" in q and "total" in q:
        return 'SELECT COUNT(*) FROM "ItemInInvoice";'
    if "diskon item invoice" in q:
        return 'SELECT SUM("discount_per_item") FROM "ItemInInvoice";'
    if "produk kategori elektronik" in q:
        return 'SELECT COUNT(*) FROM "Product" WHERE "category" = \'Elektronik\';'
    if "produk brand samsung" in q:
        return 'SELECT COUNT(*) FROM "Product" WHERE "brand_name" = \'Samsung\';'
    if "absensi izin" in q:
        return 'SELECT COUNT(*) FROM "EmployeeAttendance" WHERE "absence_status" = \'Izin\';'
    if "invoice cash" in q:
        return 'SELECT COUNT(*) FROM "Invoice" WHERE "payment_method" = \'Cash\';'
    if "produk stok habis" in q:
        return 'SELECT COUNT(*) FROM "Product" WHERE "product_quantity" = 0;'

    return None

# --- Final Summarizer for Natural Answer ---
system_summary = SystemMessagePromptTemplate.from_template("""
You are a polite assistant. 
- Respond in Bahasa Indonesia if the question is Indonesian.
- Otherwise, respond in English.
- Summarize the database result naturally and clearly.
""")

human_summary = HumanMessagePromptTemplate.from_template("""
Question: {question}
Result: {result}
""")

template_summary = ChatPromptTemplate.from_messages([system_summary, human_summary])
chain_summary = template_summary | llm | StrOutputParser()

import ast

def summarize_answer(question, result):
    """Bersihkan hasil SQL dan buat jawaban natural bahasa manusia."""

    # 1. Parse result string (e.g., '[(25,)]') menjadi list of tuple
    try:
        parsed_result = ast.literal_eval(result) if isinstance(result, str) else result
    except:
        parsed_result = result

    # 2. Ambil value yang benar (angka atau teks dari tuple/list)
    value = None
    if isinstance(parsed_result, list) and parsed_result:
        if isinstance(parsed_result[0], (tuple, list)):
            value = parsed_result[0][0]
        else:
            value = parsed_result[0]
    elif isinstance(parsed_result, (tuple, list)):
        value = parsed_result[0]
    else:
        value = parsed_result

    # 3. Handle empty, None, atau kosong
    if value is None or value == '':
        return "Maaf, tidak ada data yang ditemukan untuk pertanyaan tersebut."

    # 4. Format angka
    try:
        if isinstance(value, (int, float)):
            value = f"{int(value):,}".replace(",", ".")
        else:
            value = str(value)
    except:
        value = str(value)

    q = question.lower()
    if "invoice" in q:
        return f"Terdapat total {value} invoice di dalam database."
    elif "produk" in q:
        return f"Ada total {value} produk yang tercatat di database."
    elif "employee" in q or "karyawan" in q:
        return f"Ada {value} karyawan yang tercatat di database."
    elif "omzet" in q or "sales" in q:
        return f"Total sales omzet adalah sebesar Rp {value}."
    elif "gaji" in q:
        return f"Total gaji yang dibayarkan adalah Rp {value}."
    elif "bonus" in q:
        return f"Total bonus karyawan adalah Rp {value}."
    else:
        return f"Hasilnya adalah {value}."

# --- FULL CHAIN EXECUTION ---
@chain
def process_question(input):
    question = input["question"]
    # print(f"\n❓ Your Question: {question}\n")

    # 1. Check predefined fast queries
    query = predefined_query(question)
    if query:
        print(f"⚡ Using Predefined Query:\n{query}\n")
    else:
        # 2. If no match, use LLM generator
        query = chain_sql.invoke({"question": question})
        query = query.strip()
        query = query.replace('`', '"').replace('‘', '"').replace('’', '"').replace('“', '"').replace('”', '"')
        if "COUNT(*" in query and not "COUNT(*)" in query:
            query = query.replace("COUNT(*", "COUNT(*)")
        if "COUNT(* FROM" in query:
            query = query.replace("COUNT(* FROM", "COUNT(*) FROM")

        print(f"🛠️ Generated SQL Query:\n{query}\n")

    # 3. Validate SQL
    if not is_valid_sql(query):
        print(f"❌ Invalid SQL syntax detected:\n{query}\n")
        return {"final_answer": "Maaf, terjadi kesalahan pada query SQL."}

    # 4. Execute SQL
    try:
        result = db.run(query)
        print(f"✅ SQL Executed: {result}\n")
    except Exception as e:
        print(f"❌ SQL Error: {e}\n")
        return {"final_answer": "Maaf, terjadi kesalahan saat mengambil data dari database."}

    # 5. Summarize Final Answer
    final_text = summarize_answer(question, str(result))
    return {"final_answer": final_text}

# --- CLI Demo if running directly ---
if __name__ == "__main__":
    while True:
        user_input = input("\n💬 Masukkan pertanyaanmu: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        output = process_question.invoke({"question": user_input})
        print("\n🎯 FINAL OUTPUT:", output)