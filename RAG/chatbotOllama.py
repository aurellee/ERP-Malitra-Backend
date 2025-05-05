
# def text_to_mysql_query(prompt):
#     # Gunakan model yang tepat di Ollama
#     model = "mistral"  # atau "llama3", "codellama", tergantung yang kamu install di ollama
#     system_prompt = (
#         "You are a professional SQL assistant. "
#         "Translate the following instruction into a valid MySQL query only. "
#         "No explanations, no introductions, just return the SQL code.\n"
#     )

#     # Panggil Ollama API
#     response = ollama.chat(
#         model=model,
#         messages=[
#             {"role": "system", "content": system_prompt},
#             {"role": "user", "content": prompt}
#         ]
#     )

#     # Ambil hasil dari Ollama
#     query = response['message']['content'].strip()
#     return query

# # Contoh pemakaian
# if __name__ == "__main__":
#     instruction = "Select all employees who were hired after 2020"
#     mysql_query = text_to_mysql_query(instruction)
#     print("Generated MySQL Query:")
#     print(mysql_query)


import os
from dotenv import load_dotenv
import ollama

from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate

from langchain_core.tools import tool

os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

load_dotenv()

llm = ChatOllama(model='gemma3:4b', base_url='http://localhost:11434')


from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5433/erpmalitra")

db.dialect
db.get_usable_table_names()

db.run('SELECT * FROM "Employee" LIMIT 5')





from langchain.chains import create_sql_query_chain
sql_chain = create_sql_query_chain(llm, db)

# sql_chain.get_prompts()[0].pretty_print()
sql_chain

question = "how many employees are there? You MUST RETURN ONLY ONE POSTGRES QUERY."
response = sql_chain.invoke({'question': question})
print(response)

from scripts.llm import ask_llm
from langchain_core.runnables import chain
 
@chain
def get_correct_sql_query(input):
    context = input['context']
    question = input['question']

    instruction = """
        Use above context to fetch the correct SQL query for following question 
        {}

        Do not enclose query in ```sql and do not write preamble and explanation.
        You MUST return only single SQL query.
    """.format(question)

    def is_valid_sql(query: str) -> bool:
        query = query.strip().lower()
        # Check if it starts with basic SQL keywords
        return query.startswith(("select", "insert", "update", "delete"))

    response = ask_llm(context=context, question= question)

    print("Response from LLM:")
    print(response)

    response = response.replace('`', '"')  # replace backticks to double quote
    response = response.replace('‘', '"').replace('’', '"')  # replace weird quotes if any
    response = response.replace('“', '"').replace('”', '"')  # replace weird double quotes

    if is_valid_sql(response):
        try:
            result = db.run(response)
            print("✅ SQL executed successfully:")
            print(result)
        except Exception as e:
            print(f"❌ Failed to execute SQL: {str(e)}")
    else:
        print("⚠️ Response was not a SQL query. Here's the message from the LLM:")
        print(response)

    return response

response = get_correct_sql_query.invoke({'context': response, 'question': question})
db.run(response)



from langchain_community.tools import QuerySQLDataBaseTool

execute_query = QuerySQLDataBaseTool(db=db)

sql_query = create_sql_query_chain(llm, db)

final_chain = (
    {'context': sql_query, 'question': RunnablePassthrough()}
    | get_correct_sql_query
    | execute_query
)

question = "how many invoices are there? You MUST RETURN ONLY ONE POSTGRES QUERY."

response = final_chain.invoke({'question': question})
print(response)






from langchain_community.agent_toolkits import SQLDatabaseToolkit

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()
print(tools)

from langchain_core.messages import SystemMessage

SQL_PREFIX = """You are an agent designed to interact with a POSTGRES database.
Given an inpuf question, create a syntactically correct POSTGRES query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
You can only use the following tables:
- "Invoice"
- "Product"
- "Employee"
- "EmployeeAttendance"
- "EmployeePayroll"
- "Chatbot"
- "Product"
- "DailySales"
- "EkspedisiMasuk"
- "EmployeeBenefits"
- "ItemInInvoice"
- "User"
                                                           
IMPORTANT:
- Always use exactly the table names above.  
Then you should query the schema of the most relevant tables. You MUST RETURN ONLY ONE POSTGRES QUERY."""

system_message = SystemMessage(content=SQL_PREFIX)


from langchain_core.messages import HumanMessage
from langgraph.prebuilt import create_react_agent

agent_executor = create_react_agent(llm, tools, state_modifier=system_message, debug=True)

question = "how many products are there? You MUST RETURN ONLY MY POSTGRES QUERIES."

agent_executor.invoke({"messages":[HumanMessage(content=question)]})













# import os
# from dotenv import load_dotenv
# from langchain_ollama import ChatOllama
# from langchain_core.output_parsers import StrOutputParser
# from langchain_core.runnables import chain, RunnablePassthrough
# from langchain_core.messages import HumanMessage
# from langchain_community.utilities import SQLDatabase
# from scripts.llm import ask_llm, summarize_answer

# # Load environment
# load_dotenv()
# os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# # Initialize LLM
# llm = ChatOllama(model="deepseek-r1:1.5b", base_url="http://localhost:11434")

# # Connect to Database
# db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5432/erpmalitra")

# # --- Chain Definitions ---

# @chain
# def generate_sql(input):
#     question = input["question"]
#     raw_sql = ask_llm(context="", question=question)
    
#     # Clean generated SQL
#     sql_query = raw_sql.strip()
#     sql_query = sql_query.replace('`', '"')
#     sql_query = sql_query.replace('‘', '"').replace('’', '"')
#     sql_query = sql_query.replace('“', '"').replace('”', '"')
#     sql_query = sql_query.replace("double_quote(", "").replace(")", "")

#     # Fix COUNT(* syntax
#     if "COUNT(*" in sql_query and not "COUNT(*)" in sql_query:
#         sql_query = sql_query.replace("COUNT(*", "COUNT(*)")

#     # ✅ NEW: Fix SUM(...) parentheses
#     sql_query = fix_sum_parentheses(sql_query)

#     print(f"\n🛠️ Generated SQL Query:\n{sql_query}\n")

#     return {"query": sql_query, "original_question": question}

# def fix_sum_parentheses(query):
#     import re
#     pattern = r'SUM\(([^)]+?) FROM'
#     fixed_query = re.sub(pattern, r'SUM(\1) FROM', query)
#     return fixed_query


# @chain
# def execute_sql(input):
#     query = input["query"]

#     # Basic guard
#     if not query.lower().startswith("select"):
#         print(f"❌ Invalid Query Generated: {query}")
#         return {"result": None, "original_question": input["original_question"], "error": "Invalid SQL."}

#     try:
#         result = db.run(query)
#         print(f"✅ SQL Executed Successfully: {result}\n")
#         return {"result": result, "original_question": input["original_question"]}
#     except Exception as e:
#         print(f"❌ Error Executing SQL: {e}\n")
#         return {"result": None, "original_question": input["original_question"], "error": str(e)}


# @chain
# def summarize_response(input):
#     question = input["original_question"]
#     result = input.get("result")

#     if not result:
#         return {"final_answer": "Maaf, terjadi kesalahan saat mengambil data dari database."}

#     try:
#         if isinstance(result, list) and len(result) > 0:
#             answer_data = result[0][0] if isinstance(result[0], tuple) else result[0]
#         else:
#             answer_data = result

#         print(f"📊 Raw SQL Result: {answer_data}\n")

#         # Final rephrased response
#         final_text = summarize_answer(question, str(answer_data))
#         print(f"📝 Final Rephrased Response: {final_text}\n")
#         return {"final_answer": final_text}
#     except Exception as e:
#         print(f"❌ Error Summarizing Answer: {e}\n")
#         return {"final_answer": "Maaf, terjadi kesalahan saat merangkum jawaban."}


# # --- Full Pipeline ---
# full_chain = (
#     {"question": RunnablePassthrough()}
#     | generate_sql
#     | execute_sql
#     | summarize_response
# )

# # --- CLI Runner ---
# if __name__ == "__main__":
#     question = "berapa banyak total invoice di database?"
#     output = full_chain.invoke({"question": question})
#     print("\n🎯 FINAL OUTPUT:", output)

















# # Load environment
# os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'
# load_dotenv()

# # Connect LLM
# llm = ChatOllama(model='llama3.2', base_url='http://localhost:11434')

# # Connect Database
# db = SQLDatabase.from_uri(os.getenv("POSTGRES_URI"))

# # Create SQL Query Generator Chain
# sql_query_chain = create_sql_query_chain(llm, db)

# # SQL Execution Tool
# execute_query = QuerySQLDataBaseTool(db=db)

# # Format SQL Corrector
# @chain
# def correct_and_execute_sql(input):
#     context = input['context']
#     question = input['question']

#     def is_valid_sql(query):
#         query = query.strip().lower()
#         return query.startswith(("select", "insert", "update", "delete"))

#     from scripts.llm import ask_llm
#     sql = ask_llm(context=context, question=question)

#     print(f"🔎 SQL generated by LLM:\n{sql}\n")

#     # Cleaning characters
#     sql = sql.replace('`', '"').replace('‘', '"').replace('’', '"').replace('“', '"').replace('”', '"')

#     if not is_valid_sql(sql):
#         return "⚠️ Query yang dihasilkan tidak valid."

#     try:
#         results = db.run(sql)
#         print("✅ SQL executed successfully.")
#         # Format ke Bahasa Indonesia
#         if isinstance(results, list):
#             count = results[0][0] if results and isinstance(results[0], (tuple, list)) else 0
#             return f"Ada total {count} hasil ditemukan di database."
#         else:
#             return str(results)
#     except Exception as e:
#         print(f"❌ SQL Execution Error: {str(e)}")
#         return f"Terjadi kesalahan saat menjalankan query."

# # Chain Final
# final_chain = (
#     {"context": sql_query_chain, "question": RunnablePassthrough()}
#     | correct_and_execute_sql
# )

# # ReAct Agent Setup (Optional kalau mau pakai agent di frontend)
# from langchain_community.agent_toolkits import SQLDatabaseToolkit

# toolkit = SQLDatabaseToolkit(db=db, llm=llm)
# tools = toolkit.get_tools()

# sql_prefix = """You are an intelligent SQL agent connected to a PostgreSQL database.
# Always generate correct PostgreSQL queries using double quotes for table and column names.
# Only use the provided tables:
# - "Invoice", "Product", "Employee", "EmployeeAttendance", "EmployeePayroll", "Chatbot", "DailySales", "EkspedisiMasuk", "EmployeeBenefits", "ItemInInvoice", "User"
# Return only valid query without explanation. Respond in short, polite Indonesian if needed."""

# system_message = SystemMessage(content=sql_prefix)
# agent_executor = create_react_agent(llm, tools, state_modifier=system_message, debug=True)

# # Example usage
# if __name__ == "__main__":
#     question = "Berapa total jumlah produk yang ada?"
#     response = final_chain.invoke({'question': question})
#     print(f"📝 Final Response:\n{response}")