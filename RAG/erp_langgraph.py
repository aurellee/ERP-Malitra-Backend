import getpass
import os



# def _set_env(key: str):
#     if key not in os.environ:
#         os.environ[key] = getpass.getpass(f"{key}:")


# _set_env("OPENAI_API_KEY")



from langchain.llms.base import LLM
from typing import Optional, List
import requests

class OllamaLLM(LLM):
    model: str = "gemma3:4b"
    base_url: str = "http://localhost:11434"  # default for Ollama
    temperature: float = 0.7

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        payload = {
            "model": self.model,
            "prompt": prompt,
            "temperature": self.temperature,
        }
        response = requests.post(f"{self.base_url}/api/generate", json=payload)
        response.raise_for_status()
        return response.json()["response"]

    @property
    def _llm_type(self) -> str:
        return "ollama-custom"
    


from langchain_ollama import ChatOllama
# llm = ChatOllama(model="gemma3:4b", temperature=0.0)
llm = ChatOllama(model="llama3:8b", temperature=0)

# @tool
# def db_query_tool(query: str) -> str:
#     """
#     Execute a SQL query against the database and get back the result.
#     If the query is not correct, an error message will be returned.
#     If an error is returned, rewrite the query, check the query, and try again.
#     """
#     result = db.run_no_throw(query)
#     if not result:
#         return "Error: Query failed. Please rewrite your query and try again."
#     return result


# try:
#     llm.bind_tools([db_query_tool])  # Will raise error if unsupported
# except NotImplementedError:
#     print("This model does not support tool binding.")



import requests

url = "https://storage.googleapis.com/benchmarks-artifacts/chinook/Chinook.db"

response = requests.get(url)

if response.status_code == 200:
    # Open a local file in binary write mode
    with open("Chinook.db", "wb") as file:
        # Write the content of the response (the file) to the local file
        file.write(response.content)
    print("File downloaded and saved as Chinook.db")
else:
    print(f"Failed to download the file. Status code: {response.status_code}")



from langchain_community.utilities import SQLDatabase

db = SQLDatabase.from_uri("postgresql+psycopg2://postgres:250524@localhost:5432/erpmalitra")
print(db.dialect)
print(db.get_usable_table_names())
db.run('SELECT * FROM "Product" LIMIT 10;')




from typing import Any

from langchain_core.messages import ToolMessage
from langchain_core.runnables import RunnableLambda, RunnableWithFallbacks
from langgraph.prebuilt import ToolNode


def create_tool_node_with_fallback(tools: list) -> RunnableWithFallbacks[Any, dict]:
    """
    Create a ToolNode with a fallback to handle errors and surface them to the agent.
    """
    return ToolNode(tools).with_fallbacks(
        [RunnableLambda(handle_tool_error)], exception_key="error"
    )


def handle_tool_error(state) -> dict:
    error = state.get("error")
    tool_calls = state["messages"][-1].tool_calls
    return {
        "messages": [
            ToolMessage(
                content=f"Error: {repr(error)}\n please fix your mistakes.",
                tool_call_id=tc["id"],
            )
            for tc in tool_calls
        ]
    }



from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI

toolkit = SQLDatabaseToolkit(db=db, llm=llm)
tools = toolkit.get_tools()

list_tables_tool = next(tool for tool in tools if tool.name == "sql_db_list_tables")
get_schema_tool = next(tool for tool in tools if tool.name == "sql_db_schema")

print(list_tables_tool.invoke(""))

print(get_schema_tool.invoke("Product"))




from langchain_core.tools import tool


@tool
def db_query_tool(query: str) -> str:
    """
    Execute a SQL query against the database and get back the result.
    If the query is not correct, an error message will be returned.
    If an error is returned, rewrite the query, check the query, and try again.
    """
    result = db.run_no_throw(query)
    if not result:
        return "Error: Query failed. Please rewrite your query and try again."
    return result


print(db_query_tool.invoke('SELECT * FROM "Product" LIMIT 10;'))



from langchain_core.prompts import ChatPromptTemplate

query_check_system = """You are a SQL expert with a strong attention to detail.
Double check the PostgreSQL query for common mistakes, including:
- Using NOT IN with NULL values
- Incorrect JOINs or missing ON clauses
- Using BETWEEN for exclusive ranges
- Quoting identifiers properly
- Casting types with PostgreSQL syntax
- Avoiding functions like NOW() without timezone awareness

If there are any of the above mistakes, rewrite the query. If there are no mistakes, just reproduce the original query.

You will call the appropriate tool to execute the PostgreSQL query after running this check."""

query_check_prompt = ChatPromptTemplate.from_messages(
    [("system", query_check_system), ("placeholder", "{messages}")]
)
query_check = query_check_prompt | llm.bind_tools(
    [db_query_tool], tool_choice="required"
)

query_check.invoke({"messages": [("user", 'SELECT * FROM "Product" LIMIT 10;')]})






from typing import Annotated, Literal

from langchain_core.messages import AIMessage
from langchain_openai import ChatOpenAI

from pydantic import BaseModel, Field
from typing_extensions import TypedDict

from langgraph.graph import END, StateGraph, START
from langgraph.graph.message import AnyMessage, add_messages


# Define the state for the agent
class State(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


# Define a new graph
workflow = StateGraph(State)


# Add a node for the first tool call
def first_tool_call(state: State) -> dict[str, list[AIMessage]]:
    return {
        "messages": [
            AIMessage(
                content="",
                tool_calls=[
                    {
                        "name": "sql_db_list_tables",
                        "args": {},
                        "id": "tool_abcd123",
                    }
                ],
            )
        ]
    }


def model_check_query(state: State) -> dict[str, list[AIMessage]]:
    """
    Use this tool to double-check if your query is correct before executing it.
    """
    return {"messages": [query_check.invoke({"messages": [state["messages"][-1]]})]}


workflow.add_node("first_tool_call", first_tool_call)

# Add nodes for the first two tools
workflow.add_node(
    "list_tables_tool", create_tool_node_with_fallback([list_tables_tool])
)
workflow.add_node("get_schema_tool", create_tool_node_with_fallback([get_schema_tool]))

# Add a node for a model to choose the relevant tables based on the question and available tables
model_get_schema = llm.bind_tools(
    [get_schema_tool]
)
workflow.add_node(
    "model_get_schema",
    lambda state: {
        "messages": [model_get_schema.invoke(state["messages"])],
    },
)


# Describe a tool to represent the end state
class SubmitFinalAnswer(BaseModel):
    """Submit the final answer to the user based on the query results."""

    final_answer: str = Field(..., description="The final answer to the user")


# Add a node for a model to generate a query based on the question and schema
query_gen_system = """You are a SQL expert with a strong attention to detail.

Given an input question, output a syntactically correct SQLite query to run, then look at the results of the query and return the answer.

DO NOT call any tool besides SubmitFinalAnswer to submit the final answer.

When generating the query:

Output the SQL query that answers the input question without a tool call.

Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.

If you get an error while executing a query, rewrite the query and try again.

If you get an empty result set, you should try to rewrite the query to get a non-empty result set. 
NEVER make stuff up if you don't have enough information to answer the query... just say you don't have enough information.

If you have enough information to answer the input question, simply invoke the appropriate tool to submit the final answer to the user.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database."""
query_gen_prompt = ChatPromptTemplate.from_messages(
    [("system", query_gen_system), ("placeholder", "{messages}")]
)
query_gen = query_gen_prompt | llm.bind_tools(
    [SubmitFinalAnswer]
)


def query_gen_node(state: State):
    message = query_gen.invoke(state)

    # Sometimes, the LLM will hallucinate and call the wrong tool. We need to catch this and return an error message.
    tool_messages = []
    if message.tool_calls:
        for tc in message.tool_calls:
            if tc["name"] != "SubmitFinalAnswer":
                tool_messages.append(
                    ToolMessage(
                        content=f"Error: The wrong tool was called: {tc['name']}. Please fix your mistakes. Remember to only call SubmitFinalAnswer to submit the final answer. Generated queries should be outputted WITHOUT a tool call.",
                        tool_call_id=tc["id"],
                    )
                )
    else:
        tool_messages = []
    return {"messages": [message] + tool_messages}


workflow.add_node("query_gen", query_gen_node)

# Add a node for the model to check the query before executing it
workflow.add_node("correct_query", model_check_query)

# Add node for executing the query
workflow.add_node("execute_query", create_tool_node_with_fallback([db_query_tool]))


# Define a conditional edge to decide whether to continue or end the workflow
def should_continue(state: State) -> Literal[END, "correct_query", "query_gen"]:
    messages = state["messages"]
    last_message = messages[-1]
    # If there is a tool call, then we finish
    if getattr(last_message, "tool_calls", None):
        return END
    if last_message.content.startswith("Error:"):
        return "query_gen"
    else:
        return "correct_query"


# Specify the edges between the nodes
workflow.add_edge(START, "first_tool_call")
workflow.add_edge("first_tool_call", "list_tables_tool")
workflow.add_edge("list_tables_tool", "model_get_schema")
workflow.add_edge("model_get_schema", "get_schema_tool")
workflow.add_edge("get_schema_tool", "query_gen")
workflow.add_conditional_edges(
    "query_gen",
    should_continue,
)
workflow.add_edge("correct_query", "execute_query")
workflow.add_edge("execute_query", "query_gen")

# Compile the workflow into a runnable
app = workflow.compile()




from IPython.display import Image, display
from langchain_core.runnables.graph import MermaidDrawMethod

display(Image(app.get_graph().draw_mermaid_png()))




messages = app.invoke(
    {"messages": [("user", "Which sales agent made the most in sales this month?")]}
)
response = app.invoke({"messages": [("user", "Tampilkan invoice yang belum dibayar")]})
print(response["messages"][-1].content)



json_str = messages["messages"][-1].tool_calls[0]["args"]["final_answer"]
json_str


for event in app.stream(
    {"messages": [("user", "Which sales agent made the most in sales this month?")]}
):
    print(event)




import json


def predict_sql_agent_answer(example: dict):
    """Use this for answer evaluation"""
    msg = {"messages": ("user", example["input"])}
    messages = app.invoke(msg)
    json_str = messages["messages"][-1].tool_calls[0]["args"]
    response = json_str["final_answer"]
    return {"response": response}



from langchain import hub
from langchain_openai import ChatOpenAI

# Grade prompt
grade_prompt_answer_accuracy = prompt = hub.pull("langchain-ai/rag-answer-vs-reference")


def answer_evaluator(run, example) -> dict:
    """
    A simple evaluator for RAG answer accuracy
    """

    # Get question, ground truth answer, chain
    input_question = example.inputs["input"]
    reference = example.outputs["output"]
    prediction = run.outputs["response"]

    # LLM grader
    # llm = llm

    # Structured prompt
    answer_grader = grade_prompt_answer_accuracy | llm

    # Run evaluator
    score = answer_grader.invoke(
        {
            "question": input_question,
            "correct_answer": reference,
            "student_answer": prediction,
        }
    )
    score = score["Score"]

    return {"key": "answer_v_reference_score", "score": score}


from langsmith.evaluation import evaluate

dataset_name = "SQL Agent Response"
try:
    experiment_results = evaluate(
        predict_sql_agent_answer,
        data=dataset_name,
        evaluators=[answer_evaluator],
        num_repetitions=3,
        experiment_prefix="sql-agent-multi-step-response-v-reference",
        metadata={"version": "Chinook, gpt-4o multi-step-agent"},
    )
except:
    print("Please setup LangSmith")




# These are the tools that we expect the agent to use
expected_trajectory = [
    "sql_db_list_tables",  # first: list_tables_tool node
    "sql_db_schema",  # second: get_schema_tool node
    "db_query_tool",  # third: execute_query node
    "SubmitFinalAnswer",
]  # fourth: query_gen


def predict_sql_agent_messages(example: dict):
    """Use this for answer evaluation"""
    msg = {"messages": ("user", example["input"])}
    messages = app.invoke(msg)
    return {"response": messages}


from langsmith.schemas import Example, Run


def find_tool_calls(messages):
    """
    Find all tool calls in the messages returned
    """
    tool_calls = [
        tc["name"] for m in messages["messages"] for tc in getattr(m, "tool_calls", [])
    ]
    return tool_calls


def contains_all_tool_calls_in_order_exact_match(
    root_run: Run, example: Example
) -> dict:
    """
    Check if all expected tools are called in exact order and without any additional tool calls.
    """
    expected_trajectory = [
        "sql_db_list_tables",
        "sql_db_schema",
        "db_query_tool",
        "SubmitFinalAnswer",
    ]
    messages = root_run.outputs["response"]
    tool_calls = find_tool_calls(messages)

    # Print the tool calls for debugging
    print("Here are my tool calls:")
    print(tool_calls)

    # Check if the tool calls match the expected trajectory exactly
    if tool_calls == expected_trajectory:
        score = 1
    else:
        score = 0

    return {"score": int(score), "key": "multi_tool_call_in_exact_order"}


def contains_all_tool_calls_in_order(root_run: Run, example: Example) -> dict:
    """
    Check if all expected tools are called in order,
    but it allows for other tools to be called in between the expected ones.
    """
    messages = root_run.outputs["response"]
    tool_calls = find_tool_calls(messages)

    # Print the tool calls for debugging
    print("Here are my tool calls:")
    print(tool_calls)

    it = iter(tool_calls)
    if all(elem in it for elem in expected_trajectory):
        score = 1
    else:
        score = 0
    return {"score": int(score), "key": "multi_tool_call_in_order"}



try:
    experiment_results = evaluate(
        predict_sql_agent_messages,
        data=dataset_name,
        evaluators=[
            contains_all_tool_calls_in_order,
            contains_all_tool_calls_in_order_exact_match,
        ],
        num_repetitions=3,
        experiment_prefix="sql-agent-multi-step-tool-calling-trajecory-in-order",
        metadata={"version": "Chinook, gpt-4o multi-step-agent"},
    )
except:
    print("Please setup LangSmith")


