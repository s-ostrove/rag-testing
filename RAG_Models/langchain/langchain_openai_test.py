import os
from langchain.chat_models import init_chat_model
from langchain_openai import OpenAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_community.document_loaders.csv_loader import CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain import hub
from langchain_core.documents import Document
from langgraph.graph import START, StateGraph
from typing_extensions import List, TypedDict
from langchain_core.prompts import ChatPromptTemplate


os.environ["OPENAI_API_KEY"] = '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' # getpass.getpass("Enter API key for OpenAI: ")
# os.environ['LANGSMITH_TRACING']=True
os.environ['LANGSMITH_ENDPOINT']="https://api.smith.langchain.com"
os.environ['LANGSMITH_API_KEY']="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"
os.environ['LANGSMITH_PROJECT']="pr-whispered-diploma-37"

# Load the models
llm = init_chat_model("gpt-4o-mini", model_provider="openai")
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
vector_store = InMemoryVectorStore(embeddings)

# Load the CSV file with documents
file_path = "/Users/Samuel/Desktop/SAMUEL MacBook/Samuel Yale/Courses/Thesis/simplegraphs/0-rels-no-gp.csv"
loader = CSVLoader(file_path=file_path)
docs = loader.load()

text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
all_splits = text_splitter.split_documents(docs)

# Index chunks
_ = vector_store.add_documents(documents=all_splits)

# Define prompt for question-answering
# prompt = hub.pull("rlm/rag-prompt")
prompt = ChatPromptTemplate([
    ("human", "You are an assistant for question-answering tasks. Use the following pieces of retrieved context to answer the question. Be very concise. If you do not know, say “I don’t know.”\nQuestion: {question}\nContext: {context}")
])
# print(prompt.format(question="Who is the grandfather of Anna?", context="hello"))

# Define state for application
class State(TypedDict):
    question: str
    context: List[Document]
    answer: str


# Define application steps
def retrieve(state: State):
    retrieved_docs = vector_store.similarity_search(state["question"], 98)
    return {"context": retrieved_docs}


def generate(state: State):
    docs_content = "\n\n".join(doc.page_content for doc in state["context"])
    messages = prompt.invoke({"question": state["question"], "context": docs_content})
    response = llm.invoke(messages)
    return {"answer": response.content}


# Compile application and test
graph_builder = StateGraph(State).add_sequence([retrieve, generate])
graph_builder.add_edge(START, "retrieve")
graph = graph_builder.compile()

response = graph.invoke({"question": "Who is the grandfather of Jessica?"})
print(response["answer"])

def eval(question:str, answer:str):
    response = graph.invoke({"question": question})
    if answer.lower() in response['answer'].lower():
        return True
    else:
        print(question, answer, response['answer'])
        return False
    
import csv
questions_path = '/Users/Samuel/Desktop/SAMUEL MacBook/Samuel Yale/Courses/Thesis/simplegraphs/0-questions-grandparents.csv'
results = []
with open(questions_path, mode='r') as file:
    reader = csv.reader(file)
    for row in reader:
        question = row[0]
        answer = row[1]
        results.append(eval(question, answer))

print('Single-Doc Retrieval Accuracy:', sum(results)/len(results))