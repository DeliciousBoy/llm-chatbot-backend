from unittest import mock
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from llm_chatbot_backend.pipelines.data_processing.nodes import (
    build_rag_context,
    clean_text,
    embed_forum_data,
    process_text,
    store_to_chroma,
)


@pytest.mark.parametrize(
    "text,expected",
    [
        ("มากกก", "มากก"),  # ลดอักษรไทยซ้ำ
        ("https://example.com", ""),  # ลบ URL
        ("เศร้าา🥲", "เศร้า"),  # ลบ emoji
        ("   ", ""),  # ลบ whitespace
    ],
)
def test_clean_text(text, expected):
    assert clean_text(None) == ""
    assert clean_text(text) == expected


def test_process_text_cleaning():
    data = [
        {
            "forum_text": "ทดสอบ ",
            "doctor_reply": "หมอตอบ ",
            "disease_text": "โรค",
            "tags": ["x"],
        }
    ]
    result = process_text(data)
    assert result[0]["forum_text"] == "ทดสอบ"
    assert result[0]["doctor_reply"] == "หมอตอบ"
    assert result[0]["disease_text"] == "โรค"


def test_process_text_skip_empty_reply():
    data = [{"forum_text": "x", "doctor_reply": "", "disease_text": "y"}]
    result = process_text(data)
    assert result == []


def test_build_rag_context():
    data = {
        "forum_text": "a",
        "doctor_reply": "b",
        "disease_text": "c",
        "tags": ["tag1", "tag2"],
    }
    context = build_rag_context(data)
    assert "คำตอบจากแพทย์" in context
    assert "โรคที่เกี่ยวข้อง" in context
    assert "แท็ก" in context
    assert "tag1" in context


@patch("llm_chatbot_backend.pipelines.data_processing.nodes.SentenceTransformer")
def test_embed_forum_data(mock_model_class):
    mock_model = MagicMock()
    mock_model.encode.return_value.tolist.return_value = [[0.1, 0.2, 0.3]]
    mock_model_class.return_value = mock_model

    data = [
        {
            "forum_text": "test content text",
            "doctor_reply": "test doctor comment",
            "disease_key": "est disease key",
            "disease_text": "test disease text",
            "tags": ["tag1", "tag2"],
            "id": "doc1",
        }
    ]
    result = embed_forum_data(data)
    assert result[0]["id"] == "doc1"
    assert result[0]["context"]
    assert result[0]["embedding"] == [0.1, 0.2, 0.3]


@patch("llm_chatbot_backend.pipelines.data_processing.nodes.chromadb.PersistentClient")
def test_store_to_chroma(mock_client_class):
    mock_collection = MagicMock()
    mock_client = MagicMock()
    mock_client.get_or_create_collection.return_value = mock_collection
    mock_client_class.return_value = mock_client

    data = [
        {
            "id": "doc1",
            "context": "some context",
            "embedding": [0.1, 0.2],
            "metadata": {"disease_key": "key", "tags": "a,b"},
        }
    ]
    result = store_to_chroma(data, "/tmp/chroma")
    assert "Stored 1 documents" in result
    mock_collection.upsert.assert_called_once()
