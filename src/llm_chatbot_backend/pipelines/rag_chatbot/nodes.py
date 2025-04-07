import chromadb
from sentence_transformers import SentenceTransformer


def retrieve_relevant_documents(user_query: str, embed_model: str, persist_path: str):
    # Load Chroma client and collection
    client = chromadb.PersistentClient(path=persist_path)
    collection = client.get_or_create_collection(name="forum_data")

    # Load embedding model
    embedding_model = SentenceTransformer(embed_model)
    query_embedding = embedding_model.encode([user_query])[0]

    # Query the collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=3,
    )

    for i in range(len(results["documents"][0])):
        reply = results["metadatas"][0][i]["doctor_reply"]
        print(f"\nResult {i + 1}")
        print("คำตอบจากแพทย์:", reply)
