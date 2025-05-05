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
    if "penjualan oli" in q and "jumlah" not in q:
        return '''
        SELECT SUM(ii.price * ii.quantity) AS total_oli_sales
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'oli';
        '''
    if "penjualan oli" in q and "jumlah" in q:
        return '''
        SELECT SUM(ii.quantity) AS total_oli_units_sold
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'oli'
        AND ii.invoice_id IS NOT NULL;
        '''
    if "penjualan ban" in q and "jumlah" not in q:
        return '''
        SELECT SUM(ii.price * ii.quantity) AS total_ban_sales
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'ban';
        '''
    if "penjualan ban" in q and "jumlah" in q:
        return '''
        SELECT SUM(ii.quantity) AS total_ban_units_sold
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'ban';
        '''
    if "penjualan aki" in q and "jumlah" not in q:
        return '''
        SELECT SUM(ii.price * ii.quantity) AS total_aki_sales
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'aki';
        '''
    if "penjualan aki" in q and "jumlah" in q:
        return '''
        SELECT SUM(ii.quantity) AS total_aki_units_sold
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'aki';
        '''
    if "penjualan campuran" in q and "jumlah" not in q:
        return '''
        SELECT SUM(ii.price * ii.quantity) AS total_campuran_sales
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'campuran';
        '''
    if "penjualan campuran" in q and "jumlah" in q:
        return '''
        SELECT SUM(ii.quantity) AS total_campuran_units_sold
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'campuran';
        '''
    if "penjualan spareparts mobil" in q and "jumlah" not in q:
        return '''
        SELECT SUM(ii.price * ii.quantity) AS total_spareparts_mobil_sales
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'spareparts mobil';
        '''
    if "penjualan spareparts mobil" in q and "jumlah" in q:
        return '''
        SELECT SUM(ii.quantity) AS total_spareparts_mobil_units_sold
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'spareparts mobil';
        '''
    if "penjualan spareparts motor" in q and "jumlah" not in q:
        return '''
        SELECT SUM(ii.price * ii.quantity) AS total_spareparts_motor_sales
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'spareparts motor';
        '''
    if "penjualan spareparts motor" in q and "jumlah" in q:
        return '''
        SELECT SUM(ii.quantity) AS total_spareparts_motor_units_sold
        FROM "ItemInInvoice" ii
        JOIN "Product" p ON ii.product_id = p.product_id
        WHERE LOWER(p.category) = 'spareparts motor';
        '''
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

# 4. General AI fallback
system_general = SystemMessagePromptTemplate.from_template("""
You are a smart assistant specialized in business and finance. Answer clearly and politely.
""")
human_general = HumanMessagePromptTemplate.from_template("{question}")
chain_general = ChatPromptTemplate.from_messages([system_general, human_general]) | llm | StrOutputParser()


import ast

def summarize_answer(question, result):
    """Bersihkan hasil SQL dan buat jawaban natural bahasa manusia."""

    # 1. Parse result string (e.g., '[(25,)]') menjadi list of tuple
    try:
        parsed_result = ast.literal_eval(result) 
        # if isinstance(result, str) else result
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
    if any(keyword in question.lower() for keyword in ["penjualan", "omzet", "gaji", "harga"]) and "jumlah" not in question.lower():
        try:
            value = f"Rp {int(value):,}".replace(",", ".")
        except:
            value = str(value)
    else:
        try:
            value = f"{int(value):,}".replace(",", ".")
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
    elif "penjualan oli" in q and "jumlah" not in q:
        badge = "🛢️"
        return f"{badge} Total penjualan produk oli Anda: Rp {value}"
    elif "penjualan ban" in q and "jumlah" not in q:
        badge = "🛞"
        return f"{badge} Total penjualan produk ban Anda: Rp {value}"
    elif "penjualan campuran" in q and "jumlah" not in q:
        return f"Total penjualan produk campuran Anda: Rp {value}"
    elif "penjualan aki" in q and "jumlah" not in q:
        badge = "🔋"
        return f"{badge} Total penjualan produk aki Anda: Rp {value}"
    elif "penjualan sparepart" in q and "mobil" in q and "jumlah" not in q:
        badge = "🚗🔧"
        return f"{badge} Total penjualan spareparts mobil Anda: Rp {value}"
    elif "penjualan sparepart" in q and "motor" in q and "jumlah" not in q:
        badge = "🏍️🔧"
        return f"{badge} Total penjualan spareparts motor Anda: Rp {value}"
    elif "produk" in q:
        badge = "📦"
        return f"{badge} Ada total {value} produk yang tercatat di database."
    elif "invoice" in q:
        badge = "🧾"
        return f"{badge} Terdapat total {value} invoice di dalam database."
    elif "employee" in q or "karyawan" in q:
        badge = "👨‍💼"
        return f"{badge} Ada {value} karyawan yang tercatat di database."
    elif "omzet" in q or "sales" in q:
        badge = "💰"
        return f"{badge} Total omzet penjualan adalah sebesar {value}."
    elif "gaji" in q:
        badge = "🧾"
        return f"{badge} Total gaji yang dibayarkan adalah {value}."
    elif "bonus" in q:
        badge = "🎁"
        return f"{badge} Total bonus karyawan adalah {value}."
    elif "absen" in q or "absensi" in q:
        badge = "📋"
        return f"{badge} Total absensi yang tercatat: {value}"
    elif "penjualan oli" in q and "jumlah" in q:
        return f"🛢️ Telah terjual {value} unit produk kategori oli dari semua invoice tercatat di sistem."
    elif "penjualan ban" in q and "jumlah" in q:
        return f"🛞 Telah terjual {value} unit produk kategori ban dari semua invoice tercatat di sistem."
    elif "penjualan aki" in q and "jumlah" in q:
        return f"🔋 Telah terjual {value} unit produk kategori aki dari semua invoice tercatat di sistem."
    elif "penjualan campuran" in q and "jumlah" in q:
        return f"Telah terjual {value} unit produk kategori campuran dari semua invoice tercatat di sistem."
    elif "penjualan spareparts mobil" in q and "jumlah" in q:
        return f"🚗🔧 Telah terjual {value} unit produk kategori spareparts mobil dari semua invoice tercatat di sistem."
    elif "penjualan spareparts motor" in q and "jumlah" in q:
        return f"🏍️🔧 Telah terjual {value} unit produk kategori spareparts motor dari semua invoice tercatat di sistem."
    else:
        return f"Hasilnya adalah {value}."

# --- FULL CHAIN EXECUTION ---
from typing import Any, Optional, List, Dict, Tuple, Union

ERP_KEYWORDS = [
    "produk", "invoice", "employee", "gaji", "bonus", "absensi", "sales", "omzet", "kategori",
    "brand", "item", "dailysales", "ekspedisi", "payroll", "quantity", "status", "jumlah", "total",
    "pengeluaran", "pemasukan", "transaksi"
]

def is_internal_erp_question(q: str) -> bool:
    q = q.lower()
    return any(word in q for word in ERP_KEYWORDS)

# 1. Tambah deteksi pertanyaan yang minta perbandingan
def is_comparative_question(question):
    question = question.lower()
    return any(keyword in question for keyword in ["bandingkan", "compare", "dibandingkan", "lebih baik", "lebih tinggi", "vs"])

def extract_location_from_question(q: str) -> Optional[str]:
    locations = [
        "sulawesi utara", "sulawesi selatan", "daerah istimewa yogyakarta", "kepulauan riau",
        "jakarta", "bandung", "surabaya", "bali", "yogyakarta",
        "makassar", "medan", "sulawesi", "papua", "manado", "kalimantan", "sumatera", "jawa", "indonesia"
    ]
    q_lower = q.lower()
    for loc in locations:
        if loc in q_lower:
            return loc.title()
    return "Dunia"

# 2. Fungsi untuk ambil jawaban dari general knowledge
from langchain_core.prompts import ChatPromptTemplate

def compare_with_general_knowledge(internal_summary, question, location):
    # location = extract_location_from_question(question)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an analytical assistant who compares company database insights with regional trends."),
        ("human", f"""
Pertanyaan pengguna: {question}

Lokasi geografis yang dimaksud: {location}

Data internal perusahaan:
{internal_summary}

Tolong bandingkan hasil data internal tersebut dengan tren penjualan di wilayah tersebut, menggunakan pengetahuanmu.

Format jawaban:
- 💡 Ringkasan internal
- 🌍 Ringkasan tren eksternal wilayah {location}
- ⚖️ Kesimpulan perbandingan
""")
    ])
    chain = prompt | llm | StrOutputParser()
    return chain.invoke({})


@chain
def process_question(input):
    question = input["question"]

    # 1. Check: ERP DB-related or general knowledge?
    if is_internal_erp_question(question):
        print(f"📦 Internal ERP question detected.")
        
        # a. Try predefined fast query
        query = predefined_query(question)
        if not query:
            # b. Generate using LLM
            query = chain_sql.invoke({"question": question}).strip()

        # c. Validate
        if not is_valid_sql(query):
            return {"final_answer": "Maaf, terjadi kesalahan pada query SQL."}

        # d. Run SQL
        try:
            result = db.run(query)
            # Check if result is empty or None
            if not result or result in [[], [(None,)], None]:
                print("🔍 No internal data found. Using external knowledge fallback.")
                external = llm.invoke(question)
                return {
                    "final_answer": (
                        "📦 Maaf, tidak ada data dalam database Malitra yang ditemukan untuk pertanyaan tersebut.\n\n"
                        f"🌍 Namun berikut adalah jawaban berdasarkan pengetahuan umum:\n\n{external}"
                    )
                }
        except Exception as e:
            print(f"❌ SQL Error: {e}")
            external = llm.invoke(question)
            return {
                "final_answer": (
                    "📦 Maaf, terjadi kesalahan saat mengambil data dari database Malitra.\n\n"
                    f"🌍 Namun berikut adalah jawaban berdasarkan pengetahuan umum:\n\n{external}"
                )
            }

        # 6. Summarize internal database answer
        final_text = summarize_answer(question, str(result))

        # 7. Tambah perbandingan jika itu comparative
        if is_comparative_question(question):
            location = extract_location_from_question(question)  # ← tambahkan lokasi
            try:
                comparison_text = compare_with_general_knowledge(final_text, question, location)
                return {"final_answer": comparison_text}
            except Exception as e:
                return {
                    "final_answer": f"{final_text}\n\n⚠️ Tapi terjadi kesalahan saat mencoba membandingkan: {e}"
                }

        return {"final_answer": final_text}
    
    else:
        print(f"🌍 General knowledge question detected. Using external LLM.")
        answer = llm.invoke(question)
        return {"final_answer": answer}

# --- CLI Demo if running directly ---
if __name__ == "__main__":
    while True:
        user_input = input("\n💬 Masukkan pertanyaanmu: ")
        if user_input.lower() in ["exit", "quit"]:
            break
        output = process_question.invoke({"question": user_input})
        print("\n🎯 FINAL OUTPUT:", output)