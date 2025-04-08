import logging
import re

import chromadb
from chromadb.utils import embedding_functions
from pythainlp.util import normalize
from sentence_transformers import SentenceTransformer

logging.getLogger("kedro.io.data_catalog").setLevel(logging.WARNING)


def clean_text(text: str) -> str:
    """Clean unwanted characters, URL, and normalize Thai text."""

    if not isinstance(text, str):
        return ""

    text = normalize(text)
    text = re.sub(r"https?://\S+", "", text)
    text = re.sub(
        r"[^\u0E00-\u0E7F\w\s.,!?']", "", text
    )  # Keep Thai, basic punctuations
    text = re.sub(r"\s+", " ", text)  # Collapse multiple whitespace
    text = re.sub(r"([ก-๙])\1{1,}", r"\1\1", text)  # Reduce repeated Thai chars

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

    contexts = [build_rag_context(item) for item in data_list]
    embeddings = model.encode(contexts, batch_size=32, show_progress_bar=True).tolist()

    embedded_data = []
    for item, context, embedding in zip(data_list, contexts, embeddings):
        embedded_data.append(
            {
                "id": item.get("id") or f"doc_{hash(context)}",
                "embedding": embedding,
                "context": context,
                "metadata": {
                    "disease_key": item["disease_key"],
                    "tags": ", ".join(item["tags"]),
                },
            }
        )

    return embedded_data


def store_to_chroma(embedded_data: list[dict], persist_path: str) -> str:
    client = chromadb.PersistentClient(path=persist_path)
    collection = client.get_or_create_collection(name="forum_data")

    ids = [item["id"] for item in embedded_data]
    documents = [item["context"] for item in embedded_data]
    embeddings = [item["embedding"] for item in embedded_data]
    ids = [item["id"] for item in embedded_data]
    metadatas = [item["metadata"] for item in embedded_data]

    collection.upsert(
        ids=ids, documents=documents, embeddings=embeddings, metadatas=metadatas
    )

    return f"Stored {len(documents)} documents to ChromaDB at {persist_path}"
