# ✅ Full Final Refactor Version - ollama_chatbot.py
# ollama_chatbot.py

# ollama_chatbot.py

import os
from dotenv import load_dotenv
from langchain_core.runnables import RunnablePassthrough, chain
from langchain_community.utilities import SQLDatabase
from scripts.llm import ask_llm, is_valid_sql, summarize_answer
import sqlparse

# --- Load Environment ---
load_dotenv()
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

# --- Connect to Database ---
db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5432/erpmalitra")

# --- Chain Definitions ---
@chain
def generate_sql(input):
    
    question = input["question"]
    print(f"\n❓ Your Question: {question}\n")

    # Generate raw SQL from LLM
    raw_sql = ask_llm(question)
    sql_query = raw_sql.strip()

    # Minor auto clean if model hallucinate weird characters
    sql_query = sql_query.replace('`', '"').replace('‘', '"').replace('’', '"')
    sql_query = sql_query.replace('“', '"').replace('”', '"')
    if "COUNT(*" in sql_query and not "COUNT(*)" in sql_query:
        sql_query = sql_query.replace("COUNT(*", "COUNT(*)")
    if "COUNT(* FROM" in sql_query:
        sql_query = sql_query.replace("COUNT(* FROM", "COUNT(*) FROM")
    if sql_query.lower().startswith('"""sql'):
        sql_query = sql_query[5:].strip()
    if sql_query.endswith('"""'):
        sql_query = sql_query[:-3].strip()

    print(f"🛠️ Generated SQL Query:\n{sql_query}\n")
    
    return {"query": sql_query, "original_question": question}

@chain
def validate_and_execute_sql(input):
    query = input["query"]
    original_question = input["original_question"]

    # Validate PostgreSQL syntax
    if not is_valid_sql(query):
        print(f"❌ Invalid SQL syntax detected: {query}\n")
        return {"result": None, "original_question": original_question, "error": "Invalid PostgreSQL query."}

    if not query.lower().startswith("select"):
        print(f"❌ Non-SELECT query rejected: {query}\n")
        return {"result": None, "original_question": original_question, "error": "Only SELECT queries allowed."}

    try:
        result = db.run(query)
        print(f"✅ SQL Executed Successfully: {result}\n")
        return {"result": result, "original_question": original_question}
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}\n")
        return {"result": None, "original_question": original_question, "error": str(e)}

@chain
def summarize_result(input):
    result = input.get("result")
    question = input.get("original_question")

    if not result:
        return {"final_answer": "Maaf, terjadi kesalahan saat mengambil data dari database."}

    try:
        if isinstance(result, list) and len(result) > 0:
            answer_data = result[0][0] if isinstance(result[0], tuple) else result[0]
        else:
            answer_data = result

        print(f"📊 Raw SQL Result: {answer_data}\n")

        # Summarize to natural human language
        final_text = summarize_answer(question, str(answer_data))
        print(f"📝 Final Rephrased Response: {final_text}\n")
        return {"final_answer": final_text}
    except Exception as e:
        print(f"❌ Error Summarizing Answer: {e}\n")
        return {"final_answer": "Maaf, terjadi kesalahan saat merangkum jawaban."}

# --- Full pipeline ---
full_chain = (
    {"question": RunnablePassthrough()}
    | generate_sql
    | validate_and_execute_sql
    | summarize_result
)

# --- CLI Testing Mode ---
if __name__ == "__main__":
    question = input("💬 Masukkan pertanyaanmu: ")
    output = full_chain.invoke({"question": question})
    print("\n🎯 FINAL OUTPUT:", output)