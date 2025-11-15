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


# Qdrant Config
QDRANT_HOST = os.getenv("LOCALHOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
QDRANT_COLLECTION_NAME= os.getenv("QDRANT_COLLECTION_NAME")

#Qdrant Config Client
qdrant_url= f"http://{QDRANT_HOST}:{QDRANT_PORT}"
qdrant_client = QdrantClient(
    url=qdrant_url,
    prefer_grpc=False,
    check_compatibility=False
)

print("RAG (Retrieval Augmented Generative) is RUNNING UP!!!")
print("Please Wait!\n")


# Embedding Model
embedding = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},  
    encode_kwargs={"normalize_embeddings": True}
)

# Qdrant Vector Database Config
db= QdrantVectorStore(
    client=qdrant_client,
    embedding= embedding,
    collection_name='Food_Collection_bge-m3',
    distance=models.models.Distance.DOT
)

# Retriever
retriever = db.as_retriever(
    search_type="similarity_score_threshold", 
    search_kwargs={
        "score_threshold": 0.25,
        "k": 5,
    }
)

GROQ_API_KEY=os.getenv("GROQ_API_KEY")

# Groq Client Config
groq_client = ChatGroq(
    api_key=GROQ_API_KEY,
    model="llama-3.1-8b-instant"
)

# Prompt Template
prompt_template = """
You are an intelligent assistant tasked with answering user queries based on provided context. 
Use the following context to respond to the user's question.

Context:
{context}

Question:
{query}

Answer:
"""


prompt = ChatPromptTemplate.from_template(prompt_template)

# Get User input
user_state = True
while user_state:
    query = input("Input Question: ")
    # Process Pipeline from query -> response
    chain = (
        {"context": retriever, "query" : RunnablePassthrough()}
        | prompt
        | groq_client
        | StrOutputParser()
    )

    # Invoke LLM then Print the response
    response = chain.invoke(query)
    print("Response:", response)
    print("\n\nDo you want to ask again?")
    user_inp = input()
    if user_inp == "no" or user_inp == "tidak":
        user_state = False
        print("Thank you!")