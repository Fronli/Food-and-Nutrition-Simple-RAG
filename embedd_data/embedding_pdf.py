import os
from dotenv import load_dotenv
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_loaders import CSVLoader, PyPDFLoader
from qdrant_client import QdrantClient, models
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
load_dotenv()

QDRANT_HOST = os.getenv("QDRANT_HOST")
QDRANT_PORT = os.getenv("QDRANT_PORT")

#Qdrant Config Client
qdrant_client = QdrantClient(
    host=QDRANT_HOST,
    port=QDRANT_PORT,
    check_compatibility=False
)


model_name = "BAAI/bge-large-en"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': True}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
)

qdrant_url= f"http://{QDRANT_HOST}:{QDRANT_PORT}"


loader_combined = PyPDFLoader('json_combined.pdf')
docs_combined = loader_combined.load()

loader_nutrition = PyPDFLoader('json_nutrition.pdf')
docs_nutrition = loader_nutrition.load()


# For splitting document into chunks
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,
    length_function=len,
    separators = [
        ". ", ", ", "; ", "\n"
    ]
)
# split_docs_combined = splitter.split_documents(docs_combined)
split_docs_nutrition = splitter.split_documents(docs_nutrition)

# print(f"Total combined pdf chunks after splitting: {len(split_docs_combined)}")
print(f"Total nutrition pdf chunks after splitting: {len(split_docs_nutrition)}")


# for d in split_docs_combined:
#     d.metadata["type"] = "combined"

for d in split_docs_nutrition:
    d.metadata["type"] = "nutrition"

qdrant = QdrantVectorStore.from_documents(
    documents= split_docs_nutrition,
    embedding = embeddings,
    url=qdrant_url,
    prefer_grpc=False,
    collection_name="CP-Food-Collection",
)


# # Qdrant for text collection
# qdrant = QdrantVectorStore.from_texts(
#     embed_text,
#     embeddings,
#     url=qdrant_url,
#     prefer_grpc=False,
#     collection_name="Data-Teman-Collection",
# )