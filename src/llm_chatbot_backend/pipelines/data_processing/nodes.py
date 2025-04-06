import re
import unicodedata

import chromadb

# import logger
from sentence_transformers import SentenceTransformer


def clean_text(text: str) -> str:
    """ "Clean unwanted characters, URL, and normalize Thai text."""

    if not isinstance(text, str):
        return ""

    text = re.sub(r"https?://\S+", "", text)  # Remove URL
    text = re.sub(
        r"[^\u0E00-\u0E7F\w\s.,!?']", "", text
    )  # Keep Thai, basic punctuations
    text = re.sub(r"\s+", " ", text)  # Collapse multiple whitespace
    text = re.sub(r"([ก-๙])\1{2,}", r"\1\1", text)  # Reduce repeated Thai chars
    text = unicodedata.normalize("NFC", text)  # Normalize Thai characters
    return text.strip()


def process_text(data: list[dict]) -> list[dict]:
    """Apply cleaning function to target fields in the data."""
    cleaned_data = []
    for item in data:
        forum = clean_text(item.get("forum_text", ""))
        doctor_reply = clean_text(item.get("doctor_reply", ""))
        disease_text = clean_text(item.get("disease_text", ""))

        if not doctor_reply:
            continue

        cleaned_item = {
            **item,  # Copy all original fields
            "forum_text": forum,
            "doctor_reply": doctor_reply,
            "disease_text": disease_text,
        }
        cleaned_data.append(cleaned_item)
    return cleaned_data


def build_rag_context(data) -> str:
    return f"""[คำถามจากผู้ใช้]
        {data["forum_text"]}

        [คำตอบจากแพทย์]
        {data["doctor_reply"]}

        [โรคที่เกี่ยวข้อง]
        {data["disease_text"]}

        [แท็ก]
        {", ".join(data["tags"])}
        """


def embed_forum_data(data_list: list) -> list:
    model = SentenceTransformer(
        "sentence-transformers/paraphrase-multilingual-mpnet-base-v2"
    )

    context = [build_rag_context(item) for item in data_list]
    embedding = model.encode(context, batch_size=32, show_progress_bar=True).tolist()
    embedded_data = []
    for i, (item, context, embedding) in enumerate(zip(data_list, context, embedding)):
        embedded_data.append(
            {
                "id": f"doc_{i}",
                "embedding": embedding,
                "context": context,
                "metadata": {
                    "disease_key": item["disease_key"],
                    "tags": ", ".join(item["tags"]),
                    "doctor_reply": item["doctor_reply"],
                },
            }
        )
    return embedded_data


def save_embedded(data: list[dict], filepath: str) -> str:
    ...


def store_to_chroma(embedded_data: list[dict], persist_path: str) -> str:
    client = chromadb.PersistentClient(path="data/09_chroma_db")
    collection = client.get_or_create_collection(name="forum_data")

    documents = [item["context"] for item in embedded_data]
    embeddings = [item["embedding"] for item in embedded_data]
    ids = [item["id"] for item in embedded_data]
    metadatas = [item["metadata"] for item in embedded_data]

    print(f"Before storing, collection has {collection.count()} documents.")
    collection.add(
        documents=documents, embeddings=embeddings, ids=ids, metadatas=metadatas
    )
    print(f"After storing, collection has {collection.count()} documents.")

    return f"Stored {len(documents)} documents to ChromaDB at {persist_path}"
