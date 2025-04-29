from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from pathlib import Path
import gradio as gr

# import the .env file
from dotenv import load_dotenv
load_dotenv()

# configuration
DATA_FILE = Path("data_export.json") 
BASE_DIR = Path(__file__).resolve().parent.parent

embeddings_model = OpenAIEmbeddings(model="text-embedding-3-large")

# initiate the model
llm = ChatOpenAI(temperature=0.5, model='gpt-3.5-turbo')

# connect to the chromadb
vector_store = Chroma(
    collection_name="erp_malitra_collection",
    embedding_function=embeddings_model,
    persist_directory=str(BASE_DIR / "chroma_db"),
)

# Set up the vectorstore to be the retriever
num_results = 12
retriever = vector_store.as_retriever(search_kwargs={'k': num_results})

# call this function for every message added to the chatbot
def stream_response(message, history):
    #print(f"Input: {message}. History: {history}\n")

    # retrieve the relevant chunks based on the question asked
    docs = retriever.invoke(message)

    # add all the chunks to 'knowledge'
    knowledge = ""

    for doc in docs:
        knowledge += doc.page_content+"\n\n"


    # make the call to the LLM (including prompt)
    if message is not None:

        partial_message = ""

        rag_prompt = f"""
        You are an assistent which answers questions based on knowledge which is provided to you.
        While answering, you don't use your internal knowledge, 
        but solely the information in the "The knowledge" section.
        You don't mention anything to the user about the provided knowledge.
        You are an AI assistant specialized in financial management, inventory, employees, and invoices for an ERP system.
        Task:
        - Always present answers in a clear, human-readable format.
        - Always assume currency is Indonesian Rupiah (Rp).
        - Be concise but complete.

        Always answer in:
        - Polite, empathetic tone
        - Short, clear, to-the-point style
        - Indonesian and English language.

        The question: {message}

        Conversation history: {history}

        The knowledge: {knowledge}

        Respond accurately based only on the knowledge above.

        """

        #print(rag_prompt)

        # stream the response to the Gradio App
        for response in llm.stream(rag_prompt):
            partial_message += response.content
            yield partial_message

# initiate the Gradio app
chatbot = gr.ChatInterface(stream_response, textbox=gr.Textbox(placeholder="Send to the LLM...",
    container=False,
    autoscroll=True,
    scale=7),
)

# launch the Gradio app
chatbot.launch()