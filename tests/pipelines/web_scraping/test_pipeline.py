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
    run_scraping_pipeline,
    scrape_forum_page,
)


@pytest.fixture
def mock_scrape_params() -> dict:
    return {
        "base_url": "http://fake.url?page={page}",
        "concurrent_limit": 2,
        "timeout": 10,
        "headers": {"Authorization": "Bearer token"},
    }


@pytest.fixture
def mock_forum_data():
    return {
        "forum": {
            "disease_key": "test disease key",
            "disease_text": "test disease text",
            "content_text": "test content text",
            "default_tags": [
                {
                    "name": "test tag",
                }
            ],
        },
        "doctor_comments": [{"content_text": "test doctor comment"}],
    }


@pytest.fixture
def expected_forum_result():
    return {
        "forum_text": "test content text",
        "doctor_reply": "test doctor comment",
        "disease_key": "test disease key",
        "disease_text": "test disease text",
        "tags": ["test tag"],
    }


@pytest.fixture
def mock_forum_result() -> list[dict]:
    return [
        {
            "forum_text": "test forum",
            "doctor_reply": "test reply",
            "disease_key": "key",
            "disease_text": "text",
            "tags": ["tag"],
        }
    ]


@pytest.fixture
def mock_http_forum_response() -> dict:
    return {
        "pageProps": {
            "forums": [
                {
                    "forum": {
                        "content_text": "test content text",
                        "disease_key": "test disease key",
                        "disease_text": "test disease text",
                        "default_tags": [{"name": "test tag"}],
                    },
                    "doctor_comments": [{"content_text": "test doctor comment"}],
                }
            ]
        }
    }


def test_extract_forum_info(mock_forum_data, expected_forum_result) -> None:
    result = extract_forum_info(mock_forum_data)
    assert (
        result == expected_forum_result
    ), "Extracted forum data does not match expected result"


@pytest.mark.asyncio
async def test_get_total_pages(monkeypatch):
    mock_response = {"pageProps": {"total": 12, "forums": [1, 2, 3]}}

    class MockClient:
        async def get(self, url):
            class Response:
                def raise_for_status(self):
                    pass

                def json(self):
                    return mock_response

            return Response()

    client = MockClient()
    pages = await get_total_pages(client, "http://fake.url?page={page}")
    assert pages == 4  # 12 items / 3 per page


@pytest.mark.asyncio
async def test_fetch_forum_page(monkeypatch, mock_http_forum_response):
    class MockClient:
        async def get(self, url):
            class Response:
                def raise_for_status(self):
                    pass

                def json(self):
                    return mock_http_forum_response

            return Response()

    sem = asyncio.Semaphore(1)
    result = await fetch_forum_page(
        client=MockClient(), page=1, sem=sem, base_url="http://test.url?page={page}"
    )

    assert result[0]["forum_text"] == "test content text"
    assert result[0]["doctor_reply"] == "test doctor comment"
    assert result[0]["disease_key"] == "test disease key"
    assert result[0]["disease_text"] == "test disease text"
    assert result[0]["tags"] == ["test tag"]


@pytest.mark.asyncio
async def test_scrape_forum_page(monkeypatch, mock_scrape_params, mock_forum_result):
    # Mock get_total_pages returning 2 pages
    async def mock_get_total_pages(client, base_url):
        return 2

    # Mock fetch_forum_page returning the mock_forum_result
    async def mock_fetch_forum_page(*args, **kwargs):
        return mock_forum_result

    monkeypatch.setattr(
        "llm_chatbot_backend.pipelines.web_scraping.nodes.get_total_pages",
        mock_get_total_pages,
    )
    monkeypatch.setattr(
        "llm_chatbot_backend.pipelines.web_scraping.nodes.fetch_forum_page",
        mock_fetch_forum_page,
    )

    results = await scrape_forum_page(mock_scrape_params)

    # Check if the results match the expected mock_forum_result
    assert len(results) == 2
    assert results[0]["forum_text"] == "test forum"
    assert results[1]["doctor_reply"] == "test reply"


@pytest.mark.asyncio
async def test_scrape_forum_page_missing_url():
    with pytest.raises(ValueError, match="Base URL is required."):
        await scrape_forum_page({})


@pytest.mark.asyncio
async def test_scrape_forum_page_invalid_headers(monkeypatch, mock_forum_result):
    async def mock_get_total_pages(client, base_url):
        return 1

    async def mock_fetch_forum_page(*args, **kwargs):
        return mock_forum_result

    monkeypatch.setattr(
        "llm_chatbot_backend.pipelines.web_scraping.nodes.get_total_pages",
        mock_get_total_pages,
    )
    monkeypatch.setattr(
        "llm_chatbot_backend.pipelines.web_scraping.nodes.fetch_forum_page",
        mock_fetch_forum_page,
    )

    params = {
        "base_url": "http://fake.url?page={page}",
        "concurrent_limit": 1,
        "timeout": 5,
        "headers": "not a dict",  # 👈 invalid header
    }

    results = await scrape_forum_page(params)
    assert len(results) == 1
    assert results[0]["forum_text"] == "test forum"


@pytest.mark.asyncio
async def test_get_total_pages_divide_by_zero(monkeypatch):
    mock_response = {"pageProps": {"total": 10, "forums": []}}  # len=0

    class MockClient:
        async def get(self, url):
            class Response:
                def raise_for_status(self):
                    pass

                def json(self):
                    return mock_response

            return Response()

    client = MockClient()
    pages = await get_total_pages(client, "http://fake.url?page={page}")
    assert pages == 1  # fallback


def test_run_scraping_pipeline(monkeypatch, mock_forum_result):
    async def mock_scrape_forum_page(params):
        return mock_forum_result

    monkeypatch.setattr(
        "llm_chatbot_backend.pipelines.web_scraping.nodes.scrape_forum_page",
        mock_scrape_forum_page,
    )

    params = {"base_url": "http://fake.url?page={page}"}
    result = run_scraping_pipeline(params)

    assert result == mock_forum_result
