# import openai
# import os
# from dotenv import load_dotenv

# load_dotenv()

# openai.api_key = os.getenv("OPENAI_API_KEY")  # Set di .env kamu

# # Function untuk generate response
# def ask_gpt(prompt):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a PostgreSQL expert, return only pure valid PostgreSQL queries. No explanation."},
#             {"role": "user", "content": prompt}
#         ],
#         temperature=0,
#     )
#     return response['choices'][0]['message']['content'].strip()

# # Function untuk summarize hasil
# def summarize_gpt(question, result):
#     response = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[
#             {"role": "system", "content": "You are a helpful assistant. If question is Indonesian, answer in Indonesian. If English, answer in English. Be polite and natural."},
#             {"role": "user", "content": f"Question: {question}\nResult: {result}"}
#         ],
#         temperature=0,
#     )
#     return response['choices'][0]['message']['content'].strip()


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
db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5433/erpmalitra")

# Setup LLM
llm = ChatOllama(base_url="http://localhost:11434", model="gemma3:4b")

# --- PROMPT for LLM SQL GENERATION ---
system_sql = SystemMessagePromptTemplate.from_template("""
You are a professional SQL generator specialized ONLY in PostgreSQL.

✅ Your strict rules:
- Only output 1 single valid pure PostgreSQL SELECT query.
- DO NOT give any explanation, no reasonings, no markdown, no ``` wrapping.
- DO NOT output any <think> or any meta-thinking.
- Only pure executable PostgreSQL query is allowed.
- Always use PascalCase table names: "Product", "Invoice", "Employee", etc.
- Always use snake_case for column names: "invoice_id", "amount_paid", etc.
- Always wrap identifiers (tables and columns) in double quotes (").
- Always fully close parentheses.

✅ TABLES:
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
                                                       
✅ ERP Context:
- "Invoice" records customer sales transactions with fields like "amount_paid", "sales", "mechanic".
- "Product" stores product inventory.
- "Employee" stores employee data.
- "DailySales" records daily total sales per employee.  

🚨 VERY IMPORTANT:
- If unsure or data is missing, ONLY output exactly: I'm not sure.
- DO NOT write any <think>, <step>, <reason>, or anything else besides pure SQL SELECT query.
                                                       
You must ONLY output a valid PostgreSQL query directly.                                                                                                            
""")

human_sql = HumanMessagePromptTemplate.from_template("""
ONLY generate the final pure PostgreSQL SELECT query to answer:

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

def summarize_answer(question, result):
    return chain_summary.invoke({"question": question, "result": result})

# --- FULL CHAIN EXECUTION ---
@chain
def process_question(input):
    question = input["question"]
    print(f"\n❓ Your Question: {question}\n")

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