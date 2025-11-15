import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_classic.schema import Document
import json
load_dotenv()

QDRANT_HOST = os.getenv("LOCALHOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")
qdrant_url= f"http://{QDRANT_HOST}:{QDRANT_PORT}"
dir = '../resource/'


#Qdrant Config Client
qdrant_client = QdrantClient(
    url=qdrant_url,
    check_compatibility=False,
)

# Model Config
embeddings = HuggingFaceEmbeddings(
    model_name="BAAI/bge-m3",
    model_kwargs={"device": "cpu"},     
    encode_kwargs={"normalize_embeddings": True}
)


# For splitting document into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=350,
    chunk_overlap=50,
    length_function=len,
    separators = [
        ".", "\n"
    ]
)

# Chunk Function Procces
def format_nutrients(name, nutrients):
    lines = [f"Nutrition Facts for {name}:"]
    for nutrient, value in nutrients.items():
        lines.append(f"- {nutrient}: {value}")
    return "\n".join(lines)


# Chunk Config
docs = []

with open(dir + "recipe_2.json", "r", encoding="utf-8") as f:
    data = json.load(f)

for item in data:

    recipe_name = item["name"]

    # 1. Name chunk (no split)
    docs.append(Document(
        page_content=f"Recipe Name: {recipe_name}",
        metadata={"id": recipe_name, "type": "name"}
    ))

    # 2. Step chunks
    steps_text = "\n".join(item["steps"])
    step_chunks = splitter.split_text(steps_text)

    for sc in step_chunks:
        docs.append(Document(
            page_content=sc,
            metadata={"id": recipe_name, "type": "steps"}
        ))

    # 3. Nutrition
    nutri_text = format_nutrients(recipe_name, item["nutrients"])
    docs.append(Document(
        page_content=nutri_text,
        metadata={"id": recipe_name, "type": "nutrition"}
    ))

print("Total chunks:", len(docs))

# ---- Create Qdrant Vector Store ----
qdrant_store = QdrantVectorStore(
    client=qdrant_client,
    collection_name="Food_Collection_bge-m3",
    embedding=embeddings,
    distance=models.Distance.DOT
)

# ---- Store documents (Qdrant will embed automatically) ----
texts = [doc.page_content for doc in docs]
metadatas = [doc.metadata for doc in docs]

qdrant_store.add_texts(
    texts=texts,
    metadatas=metadatas
)

print("SUCCESS: Inserted", len(texts), "chunks into Qdrant.")