# custom_prompt = PromptTemplate.from_template("""
# You are an assistant that ONLY uses the provided knowledge to answer questions.
# You are an AI assistant specialized in financial management, inventory, employees, and invoices for an ERP system.
# You are NOT allowed to use external knowledge.
# Task:
# - Always present answers in a clear, human-readable format.
# - Always assume currency is Indonesian Rupiah (Rp).
# - Be concise but complete.

# Always answer in:
# - Polite, empathetic tone
# - Short, clear, to-the-point style
# - Indonesian language.

# Conversation history:
# {history}

# User Question:
# {question}

# Relevant Knowledge:
# {context}

# Respond accurately and politely based only on the knowledge above using Indonesian Language.
# """)






# system_sql = SystemMessagePromptTemplate.from_template("""
# You are a PostgreSQL expert assistant.
# ✅ RULES:
# - Only generate ONE valid pure PostgreSQL SELECT query.
# - No explanations, no markdown, no ``` wrapping, no <think> blocks.
# - Wrap table names and column names using DOUBLE QUOTES (").
# - Table names: PascalCase, Columns: snake_case.
# - Only use these tables and columns exactly:
#   "Chatbot": "chatbot_id", "user_id", "answer", "question", "timestamp"
#   "Product": "product_id", "product_name", "product_quantity", "category", "brand_name"
#   "Invoice": "invoice_id", "invoice_date", "car_number", "invoice_status", "payment_method", "amount_paid", "discount"
#   "DailySales": "daily_sales_id", "date", "total_sales_omzet", "salary_paid", "salary_status", "employee_id", "invoice_id"
#   "Employee": "employee_id", "employee_name", "role", "hired_date", "notes"
#   "EkspedisiMasuk":  "ekspedisi_id", "date", "quantity", "purchase_price", "sale_price", "in_or_out", "product_id"
#   "ItemInInvoice": "invoice_detail_id", "discount_per_item", "quantity", "price", "invoice_id", "product_id"
#   "EmployeePayroll": "employee_payroll_id", "payment_date", "sales_omzet_amount", "salary_amount", "employee_id"
#   "EmployeeAttendance": "employee_absence_id", "date", "clock_in", "clock_out", "day_count", "absence_status", "notes", "employee_id"
#   "EmployeeBenefits": "employee_bonus_id", "date", "bonus_type", "amount", "status", "notes", "employee_id"
# ✅ Examples: 
# - SELECT COUNT(*) FROM "Product";
# - SELECT SUM("amount_paid") FROM "Invoice" WHERE "sales" = 'Ryan Prakoso';
# - SELECT SUM("total_sales_omzet") FROM "DailySales" WHERE "employee_id" = 3;                                                       
# Always return a clean valid SQL directly.                                                                           

# ✅ ERP System Context:
# - "Invoice" records customer transactions.
# - "Sales" and "Mechanic" columns in "Invoice" refer to employees(by name).
# - "DailySales" links to employees and invoices.
# - "ItemInInvoice" links "Invoice" and "Product".
# - "EmployeeAttendance" tracks employee daily clock-in and clock-out.
# - "EmployeeBenefits" stores bonuses received by employees.
# - "EmployeePayroll" tracks salary and sales omzet for employees.
# - "EkspedisiMasuk" manages incoming and outgoing product inventory.
# - "Chatbot" logs user conversations.
                                                       
# ✅ Important Behaviors:
# - If user asks about total produk, product quantity, jumlah barang ➔ Always query COUNT(*) from "Product" table.
# - Never assume products are counted from "EkspedisiMasuk" or inventory.
# - "EkspedisiMasuk" is only used for inventory movement (stok masuk/keluar), not product counts.
# - If counting total sales omzet, SUM the "amount_paid" in "Invoice" WHERE "sales" or "mechanic" matches employee name.
# - If counting product stock, COUNT entries in "Product".
# - If the user mentions "jumlah produk" or "total produk", query must be on table "Product" using COUNT(*).
# - If the user mentions "total sales" or "omzet", query must be on table "Invoice" using SUM("amount_paid").
# - If asking about "gaji", use "EmployeePayroll".
# - If checking employee bonuses, SELECT from "EmployeeBenefits".
# - Always optimize queries using JOINs correctly if needed.
# - Always LIMIT results if user only asks for few examples.
# - Do NOT invent or guess column names or tables.
# """)











# llm.py

# import os
# from dotenv import load_dotenv
# from langchain_ollama import ChatOllama
# from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# # Load Environment
# load_dotenv()
# os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# # Init LLM
# base_url = "http://localhost:11434"
# model = "deepseek-r1:1.5b"
# llm = ChatOllama(base_url=base_url, model=model)

# # For SQL Query Generation
# system_sql = SystemMessagePromptTemplate.from_template("""
# You are a highly professional database assistant specializing in PostgreSQL.
# You MUST ONLY return the direct final PostgreSQL query.
# ✅ Your strict rules:    
# - ONLY return a SINGLE valid PostgreSQL SELECT query. Focus on generating syntactically correct PostgreSQL queries only.                                       
# - Output ONLY pure VALID PostgreSQL.
# - NO explanations, NO ```PostgreSQL wrapping, NO markdown, just pure PostgreSQL.
# - Use DOUBLE QUOTES (") for identifiers (table and column names).
# - Always fully close parentheses properly.
# - ALWAYS produce fully valid PostgreSQL.
# - ONLY generate SELECT queries.
# - When asking about quantity or counting, you MUST use COUNT(*) not COUNT(column).
# - Table names must be PascalCase (e.g., "Product", "Invoice", "Employee").
# - Column names must be in lowercase (e.g., "invoice_id", "product_name", "amount_paid").
# - Table names must match exactly as listed: "Invoice", "Product", "Employee", "EmployeeAttendance", "EmployeePayroll", "Chatbot", "DailySales", "EkspedisiMasuk", "EmployeeBenefits", "ItemInInvoice"

# ✅ ALLOWED TABLES AND COLUMNS:
# Table "Chatbot":
# - "chatbot_id"
# - "user_id"
# - "answer"
# - "question"
# - "timestamp"

# Table "Product":
# - "product_id"
# - "product_name"
# - "product_quantity"
# - "category"
# - "brand_name"

# Table "Invoice":
# - "invoice_id"
# - "invoice_date"                                                       
# - "car_number"
# - "invoice_status"
# - "payment_method"
# - "amount_paid"
# - "discount"

# Table "DailySales":
# 	•	"daily_sales_id"
# 	•	"date"
# 	•	"total_sales_omzet"
# 	•	"salary_paid"
# 	•	"salary_status"
# 	•	"employee_id"
# 	•	"invoice_id"

# Table "Employee":
# 	•	"employee_id"
# 	•	"employee_name"
# 	•	"role"
# 	•	"hired_date"
# 	•	"notes"

# Table "EkspedisiMasuk":
# 	•	"ekspedisi_id"
# 	•	"date"
# 	•	"quantity"
# 	•	"purchase_price"
# 	•	"sale_price"
# 	•	"in_or_out"
# 	•	"product_id"
                                                       
# Table "ItemInInvoice":
# 	•	"invoice_detail_id"
# 	•	"discount_per_item"
# 	•	"quantity"
# 	•	"price"
# 	•	"invoice_id"
# 	•	"product_id"

# Table "EmployeePayroll":
# 	•	"employee_payroll_id"
# 	•	"payment_date"
# 	•	"sales_omzet_amount"
# 	•	"salary_amount"
# 	•	"employee_id"

# Table "EmployeeAttendance":
# 	•	"employee_absence_id"
# 	•	"date"
# 	•	"clock_in"
# 	•	"clock_out"
# 	•	"day_count"
# 	•	"absence_status"
# 	•	"notes"
# 	•	"employee_id"        

# Table "EmployeeBenefits":
# 	•	"employee_bonus_id"
# 	•	"date"
# 	•	"bonus_type"
# 	•	"amount"
# 	•	"status"
# 	•	"notes"
# 	•	"employee_id"                                                                                                                                                    

# Only use these exact column names, exactly matching spelling and casing and the table names.                          


# ✅ ERP System Context:
# - "Invoice" records customer transactions.
# - "Sales" and "Mechanic" columns in "Invoice" refer to employees (by name).
# - "DailySales" links to employees and invoices.
# - "ItemInInvoice" links "Invoice" and "Product".
# - "EmployeeAttendance" tracks employee daily clock-in and clock-out.
# - "EmployeeBenefits" stores bonuses received by employees.
# - "EmployeePayroll" tracks salary and sales omzet for employees.
# - "EkspedisiMasuk" manages incoming and outgoing product inventory.
# - "Chatbot" logs user conversations.
# - "User" stores app users.

# ✅ Important Behaviors:
# - If counting total sales omzet, SUM the "amount_paid" in "Invoice" WHERE "sales" or "mechanic" matches employee name.
# - If counting product stock, COUNT entries in "Product".
# - If the user mentions "jumlah produk" or "total produk", query must be on table "Product" using COUNT(*).
# - If the user mentions "total sales" or "omzet", query must be on table "Invoice" using SUM("amount_paid").
# - If asking about "gaji", use "EmployeePayroll".
# - If unsure, output "I'm not sure."
# - If checking employee bonuses, SELECT from "EmployeeBenefits".
# - Always optimize queries using JOINs correctly if needed.
# - Always LIMIT results if user only asks for few examples.
# - Do NOT invent or guess column names or tables.
                                                                                                                       
# ✅ Good Examples:
# - SELECT COUNT(*) FROM "Product";
# - SELECT SUM("total_sales_omzet") FROM "DailySales" WHERE "employee_id" = 3;
# - SELECT SUM("amount_paid") FROM "Invoice" WHERE "sales" = 'Ryan Prakoso' OR "mechanic" = 'Ryan Prakoso';

# 🚨 Bad Examples (forbidden):
# - SELECT COUNT(* FROM "Product";) ❌
# - ```sql SELECT * FROM "Product"; ``` ❌
# - select * from product ❌
# - select count(product) from produk;❌                                                       
                                                       
# Always double-check that your query is syntactically valid PostgreSQL.
# NEVER output incomplete PostgreSQL queries.
# If unsure or data is missing, reply "I'm not sure."    
# """)

# human_sql = HumanMessagePromptTemplate.from_template("""
# You are generating a SELECT query for a PostgreSQL ERP database based on the question below. 
# ONLY use the allowed tables ("Product", "Invoice", "Employee", etc) unless explicitly asking about Chatbot logs.

# Always assume questions about "jumlah produk", "total produk", "total barang" refer to COUNT from the "Product" table.
# Always assume questions about "total sales", "omzet", refer to SUM from the "Invoice" table.

# Question:
# {question}
# """)

# template_sql = ChatPromptTemplate.from_messages([system_sql, human_sql])
# chain_sql = template_sql | llm | StrOutputParser()

# def ask_llm(context, question):
#     sql = chain_sql.invoke({"question": question})
#     sql = sql.strip()
#     sql = sql.replace('`', '"').replace('‘', '"').replace('’', '"').replace('“', '"').replace('”', '"')
#     sql = sql.replace("double_quote(", "").replace(")", "")
#     if "COUNT(*" in sql and not "COUNT(*)" in sql:
#         sql = sql.replace("COUNT(*", "COUNT(*)")

#     if "COUNT(* FROM" in sql:
#         sql = sql.replace("COUNT(* FROM", "COUNT(*) FROM")

#     if sql.lower().startswith('"""sql'):
#         sql = sql[5:].strip()
#     if sql.endswith('"""'):
#         sql = sql[:-3].strip()

#     return sql

# # For Natural Language Final Summarization
# system_summary = SystemMessagePromptTemplate.from_template("""
# You are a polite assistant.

# - If the user's question is Indonesian, reply in Indonesian.
# - If English, reply in English.
# - Use clear, short, human-like language.
# """)

# human_summary = HumanMessagePromptTemplate.from_template("""
# Question: {question}
# Result: {result}
# """)

# template_summary = ChatPromptTemplate.from_messages([system_summary, human_summary])
# chain_summary = template_summary | llm | StrOutputParser()

# def summarize_answer(question, result):
#     return chain_summary.invoke({"question": question, "result": result})















# from langchain_ollama import ChatOllama
# from langchain_core.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
# from langchain_core.output_parsers import StrOutputParser

# # Init LLM
# base_url = "http://localhost:11434"
# model = "deepseek-r1:1.5b"
# llm = ChatOllama(base_url=base_url, model=model)

# # For SQL generation
# system_sql = SystemMessagePromptTemplate.from_template("""
# You are a professional database assistant specialized ONLY in PostgreSQL.

# ✅ STRICT RULES:
# - Only generate a single pure PostgreSQL SELECT query.
# - Never wrap your query inside markdown, no ```sql, no ``` at all.
# - Always use double quotes (") for table names and column names.
# - Table names must use PascalCase like "Product", "Invoice", "Employee".
# - Column names must use snake_case like "product_id", "invoice_date", "amount_paid".
# - When counting total rows, always use COUNT(*) without any column name inside.
# - Write SELECT COUNT(*) FROM "Product"; if asking total number of products.
# - Never add extra parentheses or extra quotes around table names.
# - Make sure all parentheses are fully closed.
# - Always output a syntactically correct, executable PostgreSQL query.
# - Only use these allowed tables:
#   "Invoice", "Product", "Employee", "EmployeeAttendance", "EmployeePayroll", "Chatbot", "DailySales", "EkspedisiMasuk", "EmployeeBenefits", "ItemInInvoice"
# - If unsure or missing information, reply exactly with: I'm not sure.

# ✅ ALLOWED TABLES AND COLUMNS:
# Table "Chatbot":
# - "chatbot_id"
# - "user_id"
# - "answer"
# - "question"
# - "timestamp"

# Table "Product":
# - "product_id"
# - "product_name"
# - "product_quantity"
# - "category"
# - "brand_name"

# Table "Invoice":
# - "invoice_id"
# - "invoice_date"                                                       
# - "car_number"
# - "invoice_status"
# - "payment_method"
# - "amount_paid"
# - "discount"

# Table "DailySales":
# 	•	"daily_sales_id"
# 	•	"date"
# 	•	"total_sales_omzet"
# 	•	"salary_paid"
# 	•	"salary_status"
# 	•	"employee_id"
# 	•	"invoice_id"

# Table "Employee":
# 	•	"employee_id"
# 	•	"employee_name"
# 	•	"role"
# 	•	"hired_date"
# 	•	"notes"

# Table "EkspedisiMasuk":
# 	•	"ekspedisi_id"
# 	•	"date"
# 	•	"quantity"
# 	•	"purchase_price"
# 	•	"sale_price"
# 	•	"in_or_out"
# 	•	"product_id"
                                                       
# Table "ItemInInvoice":
# 	•	"invoice_detail_id"
# 	•	"discount_per_item"
# 	•	"quantity"
# 	•	"price"
# 	•	"invoice_id"
# 	•	"product_id"

# Table "EmployeePayroll":
# 	•	"employee_payroll_id"
# 	•	"payment_date"
# 	•	"sales_omzet_amount"
# 	•	"salary_amount"
# 	•	"employee_id"

# Table "EmployeeAttendance":
# 	•	"employee_absence_id"
# 	•	"date"
# 	•	"clock_in"
# 	•	"clock_out"
# 	•	"day_count"
# 	•	"absence_status"
# 	•	"notes"
# 	•	"employee_id"        

# Table "EmployeeBenefits":
# 	•	"employee_bonus_id"
# 	•	"date"
# 	•	"bonus_type"
# 	•	"amount"
# 	•	"status"
# 	•	"notes"
# 	•	"employee_id"                                                                                                                                                    

# Only use these exact column names, exactly matching spelling and casing and the table names.                          
                                                       

# 🚨 IF you don't know the correct table, respond ONLY with: "I'm not sure."

# ✅ Examples:
# Good:
# SELECT COUNT(*) FROM "Product";

# Bad:
# SELECT COUNT(* FROM "Product";) ❌
# SELECT COUNT("product_id") FROM "Product"; ❌
# SELECT "product_id" FROM "product"; ❌
# """ )

# human_sql = HumanMessagePromptTemplate.from_template("""
# Generate a pure PostgreSQL SELECT query based on this question. 
# Always prioritize correct syntax, proper use of COUNT(*), SUM(), WHERE clauses.
# Do not explain, just output the SQL.

# Question:
# {question}
# """)

# template_sql = ChatPromptTemplate.from_messages([system_sql, human_sql])
# chain_sql = template_sql | llm | StrOutputParser()

# def ask_llm(context, question):
#     raw_sql = chain_sql.invoke({"question": question})
#     clean_sql = raw_sql.strip()

#     # Clean markdown
#     if clean_sql.lower().startswith('"""sql'):
#         clean_sql = clean_sql[5:].strip()
#     if clean_sql.endswith('"""'):
#         clean_sql = clean_sql[:-3].strip()

#     # Hardcore cleaning hallucination
#     clean_sql = clean_sql.replace("double_quote(", "").replace(")", "")
#     clean_sql = clean_sql.replace("‘", '"').replace("’", '"').replace("“", '"').replace("”", '"')

#     # ✨ Extra syntax fix: ensure COUNT(*) syntax
#     clean_sql = clean_sql.replace("COUNT(*", "COUNT(*)")

#     return clean_sql


# # For human-like final summarization
# system_summary = SystemMessagePromptTemplate.from_template("""
# You are a polite assistant. Based on the number result, generate a natural response.

# - If input question is in Indonesian, reply in Indonesian.
# - If input question is in English, reply in English.
# - Clear and concise.
# """)

# human_summary = HumanMessagePromptTemplate.from_template("""
# Question: {question}
# Result: {result}
# """)

# template_summary = ChatPromptTemplate.from_messages([system_summary, human_summary])
# chain_summary = template_summary | llm | StrOutputParser()

# def summarize_answer(question, result):
#     return chain_summary.invoke({"question": question, "result": result})














# # Question Answering using LLM

# from langchain_ollama import ChatOllama

# from langchain_core.prompts import (SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate)

# from langchain_core.output_parsers import StrOutputParser

# from context_generator import generate_context_description

# base_url = "http://localhost:11434"
# model = 'llama3.2'

# llm = ChatOllama(base_url=base_url, model=model)

# system_message = SystemMessagePromptTemplate.from_template("""
# You are a helpful AI assistant that writes PostgreSQL queries based ONLY on the provided context.
                                                           
# ✅ RULES you MUST follow strictly:
# - Only generate VALID PostgreSQL queries.
# - Always use DOUBLE QUOTES (") for table names and column names.
# - Always capitalize table and column names in PascalCase (first letter capitalized).
# - Never use backticks (`) or single quotes (') for identifiers.
# - Never mention MySQL, SQLite, or any non-PostgreSQL database.
# - Do NOT include ```sql or explanations. Only return the pure SQL query.
                                                           
# You can only use the following tables:
# - "Invoice"
# - "Product"
# - "Employee"
# - "EmployeeAttendance"
# - "EmployeePayroll"
# - "Chatbot"
# - "Product"
# - "DailySales"
# - "EkspedisiMasuk"
# - "EmployeeBenefits"
# - "ItemInInvoice"
# - "User"
                                                           
# IMPORTANT:
# - Always use exactly the table names above.                                                           
                                                        
# ✅ Example:
# Good: SELECT "Name" FROM "Employee";
# Bad: select * from employee;
# """)

# human_message = HumanMessagePromptTemplate.from_template("""
#                 You are a helpful AI assistant for answering database questions based on the provided context ONLY! 
#                 - If you cannot answer based on context, politely say "I'm not sure." 
#                 - If user speaks Indonesian, reply in polite Bahasa Indonesia.
#                 - If user speaks English, reply in polite English.
#                 - Format must be human-readable and empathetic.
#                             ### Context:
#                             {context}                  

#                             ### Question:
#                             {question}

#                             ### Answer:""")

# messages = [system_message, human_message]
# template = ChatPromptTemplate.from_messages(messages)

# # template
# # template.invoke({'context': context, 'question': question})

# qna_chain = template | llm | StrOutputParser()

# def ask_llm(context, question):
#     return qna_chain.invoke({'context': context, 'question': question})








# {
#   "products": [
#     {
#       "product_id": "BAN001",
#       "name": "Ban Michellin",
#       "category": "Ban",
#       "brand": "Michellin",
#       "quantity": 71
#     },
#     {
#       "product_id": "Ban011",
#       "name": "Ban F1",
#       "category": "Ban",
#       "brand": "F3",
#       "quantity": 1764
#     },
#     {
#       "product_id": "OLI001",
#       "name": "Oli Mobil",
#       "category": "Oli",
#       "brand": "Michellin",
#       "quantity": 2
#     },
#     {
#       "product_id": "TEST123",
#       "name": "Test Product",
#       "category": "Oli",
#       "brand": "Acme",
#       "quantity": 999
#     },
#     {
#       "product_id": "OLI002",
#       "name": "Ban Michelin Star Testing",
#       "category": "SpareParts Mobil",
#       "brand": "Michelin",
#       "quantity": 40
#     }
#   ],
#   "users": [
#     {
#       "id": 1,
#       "email": "michael@gmail.com",
#       "username": "michael",
#       "first_name": "",
#       "last_name": ""
#     }
#   ],
#   "employees": [
#     {
#       "employee_id": 1,
#       "name": "Aurelle",
#       "role": "Sales",
#       "hired_date": "2024-02-20",
#       "notes": "Pertama kali kerja"
#     },
#     {
#       "employee_id": 2,
#       "name": "Michael",
#       "role": "Mechanic",
#       "hired_date": "2024-03-03",
#       "notes": "Michael pacarnya Aurel"
#     }
#   ],
#   "ekspedisi": [
#     {
#       "ekspedisi_id": 2,
#       "product": {
#         "product_id": "BAN001",
#         "name": "Ban Michellin",
#         "category": "Ban",
#         "brand": "Michellin",
#         "quantity": 71
#       },
#       "qty": 100,
#       "purchase_price": 500000.0,
#       "sale_price": 900000.0,
#       "in_or_out": 1,
#       "date": "2025-04-19T09:29:14.493642+00:00"
#     },
#     {
#       "ekspedisi_id": 3,
#       "product": {
#         "product_id": "Ban011",
#         "name": "Ban F1",
#         "category": "Ban",
#         "brand": "F3",
#         "quantity": 1764
#       },
#       "qty": 90,
#       "purchase_price": 1500000.0,
#       "sale_price": 900000.0,
#       "in_or_out": 1,
#       "date": "2025-04-19T09:29:51.448866+00:00"
#     },
#     {
#       "ekspedisi_id": 4,
#       "product": {
#         "product_id": "Ban011",
#         "name": "Ban F1",
#         "category": "Ban",
#         "brand": "F3",
#         "quantity": 1764
#       },
#       "qty": 920,
#       "purchase_price": 1500000.0,
#       "sale_price": 2400000.0,
#       "in_or_out": 1,
#       "date": "2025-04-19T10:21:09.953994+00:00"
#     },
#     {
#       "ekspedisi_id": 5,
#       "product": {
#         "product_id": "OLI001",
#         "name": "Oli Mobil",
#         "category": "Oli",
#         "brand": "Michellin",
#         "quantity": 2
#       },
#       "qty": 20,
#       "purchase_price": 700000.0,
#       "sale_price": 730000.0,
#       "in_or_out": 1,
#       "date": "2025-04-23T17:20:34.240242+00:00"
#     },
#     {
#       "ekspedisi_id": 6,
#       "product": {
#         "product_id": "OLI001",
#         "name": "Oli Mobil",
#         "category": "Oli",
#         "brand": "Michellin",
#         "quantity": 2
#       },
#       "qty": 20,
#       "purchase_price": 170000.0,
#       "sale_price": 200000.0,
#       "in_or_out": 1,
#       "date": "2025-04-23T17:50:40.230561+00:00"
#     }
#   ],
#   "invoices": [
#     {
#       "invoice_id": 1,
#       "date": "2025-04-20",
#       "amount_paid": 350000.0,
#       "payment_method": "Cash",
#       "car_number": "B1234XYJ",
#       "discount": 20000.0,
#       "status": "Partially Paid",
#       "items": [
#         {
#           "detail_id": 80,
#           "product": {
#             "product_id": "BAN001",
#             "name": "Ban Michellin",
#             "category": "Ban",
#             "brand": "Michellin",
#             "quantity": 71
#           },
#           "price": 900000.0,
#           "quantity": 1,
#           "discount_per_item": 50000.0
#         },
#         {
#           "detail_id": 81,
#           "product": {
#             "product_id": "Ban011",
#             "name": "Ban F1",
#             "category": "Ban",
#             "brand": "F3",
#             "quantity": 1764
#           },
#           "price": 900000.0,
#           "quantity": 2,
#           "discount_per_item": 20000.0
#         },
#         {
#           "detail_id": 83,
#           "product": {
#             "product_id": "OLI001",
#             "name": "Oli Mobil",
#             "category": "Oli",
#             "brand": "Michellin",
#             "quantity": 2
#           },
#           "price": 730000.0,
#           "quantity": 1,
#           "discount_per_item": 0.0
#         }
#       ]
#     }
#   ],
#   "daily_sales": [
#     {
#       "daily_sales_id": 22,
#       "invoice": {
#         "invoice_id": 1,
#         "amount_paid": 350000.0,
#         "status": "Partially Paid"
#       },
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "date": "2025-04-24",
#       "omzet": 350000.0,
#       "paid": 35000.0,
#       "status": "Fully Paid"
#     }
#   ],
#   "employee_benefits": [
#     {
#       "bonus_id": 3,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-21",
#       "type": "Reimbursement",
#       "amount": 100000.0,
#       "status": "Paid",
#       "notes": "Makan Sayur"
#     },
#     {
#       "bonus_id": 4,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-21",
#       "type": "Meal Subsidy",
#       "amount": 90000.0,
#       "status": "Paid",
#       "notes": "Makan Bebek"
#     },
#     {
#       "bonus_id": 5,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-21",
#       "type": "Transport Allowance",
#       "amount": 20000.0,
#       "status": "Paid",
#       "notes": "Makan jagung"
#     },
#     {
#       "bonus_id": 6,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-21",
#       "type": "Bonus",
#       "amount": 5000.0,
#       "status": "Paid",
#       "notes": "Aurel kea bongus"
#     },
#     {
#       "bonus_id": 7,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-21",
#       "type": "Meal Subsidy",
#       "amount": 20000.0,
#       "status": "Paid",
#       "notes": "Aurel blm makan"
#     },
#     {
#       "bonus_id": 2,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-20",
#       "type": "Transport Bonus",
#       "amount": 150000.0,
#       "status": "Paid",
#       "notes": "Bonus tambahan untuk tugas luar kota"
#     }
#   ],
#   "attendance": [
#     {
#       "absence_id": 2,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "date": "2025-04-20",
#       "clock_in": "09:00:00",
#       "clock_out": "17:00:00",
#       "day_count": 1.0,
#       "status": "Present",
#       "notes": "-"
#     },
#     {
#       "absence_id": 1,
#       "employee": {
#         "employee_id": 1,
#         "name": "Aurelle",
#         "role": "Sales",
#         "hired_date": "2024-02-20",
#         "notes": "Pertama kali kerja"
#       },
#       "date": "2025-04-20",
#       "clock_in": "11:00:00",
#       "clock_out": "17:00:00",
#       "day_count": 1.0,
#       "status": "Present",
#       "notes": "-"
#     }
#   ],
#   "payroll": [
#     {
#       "payroll_id": 4,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T17:51:07.477000+00:00",
#       "sales_omzet": 100000.0,
#       "salary_amount": 10000.0
#     },
#     {
#       "payroll_id": 5,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T17:55:39.530000+00:00",
#       "sales_omzet": 100000.0,
#       "salary_amount": 10000.0
#     },
#     {
#       "payroll_id": 6,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T17:56:07.476000+00:00",
#       "sales_omzet": 100000.0,
#       "salary_amount": 10000.0
#     },
#     {
#       "payroll_id": 7,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T18:03:15.831000+00:00",
#       "sales_omzet": 100000.0,
#       "salary_amount": 10000.0
#     },
#     {
#       "payroll_id": 8,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T18:04:59.261000+00:00",
#       "sales_omzet": 100000.0,
#       "salary_amount": 10000.0
#     },
#     {
#       "payroll_id": 9,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T18:11:10.143000+00:00",
#       "sales_omzet": 200000.0,
#       "salary_amount": 20000.0
#     },
#     {
#       "payroll_id": 10,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T18:13:22.510000+00:00",
#       "sales_omzet": 200000.0,
#       "salary_amount": 20000.0
#     },
#     {
#       "payroll_id": 11,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T18:35:47.840000+00:00",
#       "sales_omzet": 300000.0,
#       "salary_amount": 10000.0
#     },
#     {
#       "payroll_id": 12,
#       "employee": {
#         "employee_id": 2,
#         "name": "Michael",
#         "role": "Mechanic",
#         "hired_date": "2024-03-03",
#         "notes": "Michael pacarnya Aurel"
#       },
#       "payment_date": "2025-04-23T18:49:31.734000+00:00",
#       "sales_omzet": 350000.0,
#       "salary_amount": 5000.0
#     }
#   ]
# }