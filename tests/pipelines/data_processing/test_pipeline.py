import pytest
from llm_chatbot_backend.pipelines.data_processing.nodes import (
    build_rag_context,
    clean_text,
    process_text,
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


# @pytest.fixture()
# def test_build_rag_context():
#     data = {
#         "forum_text": "ฉันมีอาการปวดหัว",
#         "doctor_reply": "คุณควรพักผ่อน",
#         "disease_text": "ไมเกรน",
#         "tags": ["ปวดหัว", "ไมเกรน"],
#     }
#     result = build_rag_context(data)
#     assert "[คำถามจากผู้ใช้]" in result
#     assert "[คำตอบจากแพทย์]" in result
