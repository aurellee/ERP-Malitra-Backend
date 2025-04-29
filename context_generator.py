# context_generator.py

from langchain_community.utilities import SQLDatabase

def generate_context_description():
    db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5432/erpmalitra")
    tables = db.get_usable_table_names()
    
    descriptions = []
    for table in tables:
        columns = db.get_table_info(table)
        descriptions.append(columns.strip())

    full_context = "\n\n".join(descriptions)
    return full_context