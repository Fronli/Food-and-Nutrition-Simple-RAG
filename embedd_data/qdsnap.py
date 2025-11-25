import requests

# URL Qdrant lokal
BASE_URL = "http://localhost:6333"

# Nama collection yang mau di-snapshot
collection = "Food_Collection_bge-m3"

url = f"{BASE_URL}/collections/{collection}/snapshots"

response = requests.post(url)

if response.status_code == 200:
    print("Snapshot created!")
    print(response.json())
else:
    print("Failed:", response.text)