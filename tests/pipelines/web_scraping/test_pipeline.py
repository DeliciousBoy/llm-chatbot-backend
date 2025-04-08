import asyncio
from unittest import mock
from unittest.mock import AsyncMock, patch

import httpx
import pytest
from httpx import AsyncClient
from llm_chatbot_backend.pipelines.web_scraping.nodes import (
    extract_forum_info,
    fetch_forum_page,
    get_total_pages,
)


@pytest.fixture
def mock_forum_data() -> dict[str, any]:
    return {
        "forum": {
            "disease_key": "test disease key",
            "disease_text": "test disease text",
            "content_text": "test content text",
            "default_tags": [
                {
                    "name": "test tag 1",
                }
            ],
        },
        "doctor_comments": [{"content_text": "test doctor comment"}],
    }


@pytest.fixture
def expected_forum_result() -> dict[str, any]:
    return {
        "forum_text": "test content text",
        "doctor_reply": "test doctor comment",
        "disease_key": "test disease key",
        "disease_text": "test disease text",
        "tags": ["test tag 1"],
    }


def test_extract_forum_info(mock_forum_data, expected_forum_result) -> None:
    result = extract_forum_info(mock_forum_data)
    assert (
        result == expected_forum_result
    ), "Extracted forum data does not match expected result"


# @pytest.mark.asyncio
# @patch("llm_chatbot_backend.pipelines.web_scraping.nodes.httpx.AsyncClient.get")
# @patch("llm_chatbot_backend.pipelines.web_scraping.nodes.extract_forum_info")
# async def test_fetch_forum_page(
#     mock_extract, mock_get, mock_forum_data, expected_forum_result
# ) -> None:
#     mock_response = AsyncMock()
#     mock_response.json.return_value = {"pageProps": {"forums": [mock_forum_data]}}
#     mock_response.raise_for_status.return_value = None
#     mock_get.return_value = mock_response

#     # Mock extract_forum_info to return simplified result
#     mock_extract.return_value = expected_forum_result

#     sem = asyncio.Semaphore(1)
#     client = AsyncClient()
#     base_url = "https://example.com/api?page={page}"

#     result = await fetch_forum_page(client=client, page=1, sem=sem, base_url=base_url)

#     # ✅ ตรวจว่า return ถูกต้อง
#     assert isinstance(result, list)
#     assert result == [expected_forum_result]
#     mock_get.assert_called_once()
#     mock_extract.assert_called_once_with(mock_forum_data)


@pytest.mark.asyncio
async def test_get_total_pages():
    base_url = "https://www.agnoshealth.com/_next/data/i499vlSTx42EOnWUOHBkP/th/forums/search.json?page={page}"
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
        )
    }
    timeout = httpx.Timeout(20)
    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        total_pages = await get_total_pages(client, base_url)
        # print(f"📄 Total pages: {total_pages}")
        assert total_pages > 0, "Total pages should be greater than 0"
