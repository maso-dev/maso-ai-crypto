import os
import requests
import json

# Configuration
MILVUS_URI = os.getenv("MILVUS_URI", "https://in03-9f01d93b384a0f7.serverless.gcp-us-west1.cloud.zilliz.com")
MILVUS_TOKEN = os.getenv("MILVUS_TOKEN")
MILVUS_CLUSTER_NAME = os.getenv("MILVUS_CLUSTER_NAME", "elmaso-free")
MILVUS_COLLECTION_NAME = os.getenv("MILVUS_COLLECTION_NAME", "crypto_news_rag")
FULL_COLLECTION_NAME = f"{MILVUS_CLUSTER_NAME}.{MILVUS_COLLECTION_NAME}"

def test_milvus_search():
    print("Testing Milvus search...")
    print(f"Cluster: {MILVUS_CLUSTER_NAME}")
    print(f"Collection: {MILVUS_COLLECTION_NAME}")
    print(f"Full Collection Name: {FULL_COLLECTION_NAME}")
    
    # Test 1: List collections
    print("\n1. Listing collections...")
    headers = {
        "Authorization": f"Bearer {MILVUS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    list_url = f"{MILVUS_URI}/v1/vector/collections"
    try:
        response = requests.get(list_url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            collections = response.json()
            print(f"   Collections: {collections}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 2: Get collection info
    print(f"\n2. Getting info for collection '{FULL_COLLECTION_NAME}'...")
    info_url = f"{MILVUS_URI}/v1/vector/collections/{FULL_COLLECTION_NAME}"
    try:
        response = requests.get(info_url, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            info = response.json()
            print(f"   Collection info: {json.dumps(info, indent=2)}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Test 3: Simple query to get some records
    print(f"\n3. Querying collection '{FULL_COLLECTION_NAME}'...")
    query_url = f"{MILVUS_URI}/v1/vector/search"
    query_data = {
        "collectionName": FULL_COLLECTION_NAME,
        "limit": 5,
        "outputFields": ["chunk_text", "crypto_topic", "title", "source_url"]
    }
    
    try:
        response = requests.post(query_url, json=query_data, headers=headers)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"   Found {len(result.get('data', []))} records")
            for i, record in enumerate(result.get('data', [])[:3]):
                print(f"   Record {i+1}:")
                print(f"     Title: {record.get('title', 'N/A')[:50]}...")
                print(f"     Topic: {record.get('crypto_topic', 'N/A')}")
                print(f"     URL: {record.get('source_url', 'N/A')[:50]}...")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Error: {e}")

if __name__ == "__main__":
    test_milvus_search() 
