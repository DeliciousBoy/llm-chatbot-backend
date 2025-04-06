import json
import logging
import re
import unicodedata
from pathlib import Path

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
        cleaned_item = {
            **item,  # Copy all original fields
            "forum_text": clean_text(item.get("forum_text", "")),
            "doctor_reply": clean_text(item.get("doctor_reply", "")),
            "disease_text": clean_text(item.get("disease_text", "")),
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

    embedded_data = []
    for i, item in enumerate(data_list):
        context = build_rag_context(item)
        embedding = model.encode(context).tolist()
        embedded_data.append(
            {
                "id": f"doc_{i}",
                "embedding": embedding,
                "context": context,
                "metadata": {"disease_key": item["disease_key"], "tags": item["tags"]},
            }
        )

    return embedded_data


# def clean_forum_data(input_path: Path, output_path: Path) -> None:
#     """Load, clean, and save forum data from JSON file."""
#     try:
#         with open(input_path, encoding="utf-8") as f:
#             data = json.load(f)
#         if not isinstance(data, list):
#             raise ValueError("Expected a list of forum records")
#     except Exception as e:
#         logging.error(f"Error loading input file: {e}")
#         return

#     logging.info(f"Loaded {len(data)} records from {input_path.name}")

#     cleaned_data = process_text(data)

#     try:
#         with open(output_path, "w", encoding="utf-8") as f:
#             json.dump(cleaned_data, f, ensure_ascii=False, indent=2)
#         logging.info(f"Successfully wrote cleaned data to {output_path.name}")
#     except Exception as e:
#         logging.error(f"Error writing output file: {e}")
