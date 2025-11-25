import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_groq import ChatGroq
load_dotenv()

# ==================================================
# File ini digunakan untuk main file dari RAG 
# Dimana bisa digunakan bertanya perihal Food Recipes dan Nutritions
# ==================================================

# Credential Variables
QDRANT_HOST = os.getenv("LOCALHOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
QDRANT_COLLECTION_NAME = os.getenv("QDRANT_COLLECTION_NAME")
QDRANT_CLOUD_ENDPOINT = os.getenv("QDRANT_CLOUD_ENDPOINT")
QDRANT_CLOUD_API_KEY = os.getenv("QDRANT_CLOUD_API_KEY")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")


#Qdrant Config Client
qdrant_client = QdrantClient(
    url=QDRANT_CLOUD_ENDPOINT,
    api_key= QDRANT_CLOUD_API_KEY,
    prefer_grpc=False,
    check_compatibility=False
)

print("RAG (Retrieval Augmented Generative) is RUNNING UP!!!")
print("Please Wait!\n")


# Embedding Model
model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)

# Qdrant Vector Database Config
db= QdrantVectorStore(
    client=qdrant_client,
    embedding= embeddings,
    collection_name=QDRANT_COLLECTION_NAME,
    distance=models.models.Distance.DOT
)

# Groq Client Config
groq_client = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant",
    
)

# Retriever
retriever = db.as_retriever(
    search_type="similarity_score_threshold", 
    search_kwargs={
        "score_threshold": 0.25,
        "k": 5,
    }
)


# Prompt Template
prompt_template = """
You are an intelligent assistant tasked with answering user queries based on provided context about food recipes and nutritions. It will be great if you can act like a chef or nutristionist based on the context
Use the following context to respond to the user's question. Just answer directly without explanations such as “based on context or references...”

Context:
{context}

Question:
{query}

Answer:
"""


prompt = ChatPromptTemplate.from_template(prompt_template)

chain = (
    {"context": retriever, "query" : RunnablePassthrough()}
    | prompt
    | groq_client
    | StrOutputParser()
)  


def main_invoke(query):
    response = chain.invoke(query)
    return response
    