import pytest

from llm_chatbot_backend.pipelines.data_processing.nodes import (
    build_rag_context,
)


@pytest.fixture()
def test_build_rag_context():
    data = {
        "forum_text": "ฉันมีอาการปวดหัว",
        "doctor_reply": "คุณควรพักผ่อน",
        "disease_text": "ไมเกรน",
        "tags": ["ปวดหัว", "ไมเกรน"],
    }
    result = build_rag_context(data)
    assert "[คำถามจากผู้ใช้]" in result
    assert "[คำตอบจากแพทย์]" in result
