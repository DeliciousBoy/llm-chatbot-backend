import httpx
import pytest

from llm_chatbot_backend.pipelines.web_scraping.nodes import (
    get_total_pages,
)


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


def test_dumm():
    assert True
