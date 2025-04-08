import asyncio
import logging
import math

import httpx
from tenacity import retry, stop_after_attempt, wait_fixed
from tqdm.asyncio import tqdm_asyncio

logger = logging.getLogger(__name__)


def extract_forum_info(forum_obj: dict) -> dict:
    """Extracts relevant information from the forum object.

    Args:
        forum_obj: Forum object containing the data.
    Returns:
        Extracted forum information.
    """
    forum = forum_obj.get("forum", {})
    forum_text = forum.get("content_text", "")
    doctor_comments = forum_obj.get("doctor_comments", [])
    doctor_text = doctor_comments[0].get("content_text", "") if doctor_comments else ""
    disease_key = forum.get("disease_key", "")
    disease_text = forum.get("disease_text", "")
    custom_tags = forum.get("custom_tags", [])
    default_tags = forum.get("default_tags", [])
    tags = [
        tag.get("name", "").strip()
        for tag in (custom_tags + default_tags)
        if tag.get("name", "")
    ]
    return {
        "forum_text": forum_text.strip(),
        "doctor_reply": doctor_text.strip(),
        "disease_key": disease_key.strip(),
        "disease_text": disease_text.strip(),
        "tags": tags,
    }


async def get_total_pages(client: httpx.AsyncClient, base_url: str) -> int:
    url = base_url.format(page=1)
    res = await client.get(url)
    res.raise_for_status()
    data = res.json()
    total_items = data.get("pageProps", {}).get("total", 0)
    item_per_page = len(data.get("pageProps", {}).get("forums", []))
    return math.ceil(total_items / item_per_page) if item_per_page else 1


@retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(5),  # Wait 5 seconds between attempts
    reraise=True,  # Reraise the last exception
)
async def fetch_forum_page(
    *, client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore, base_url: str
) -> list[dict]:
    """Fetches a page of forum data.

    Args:
        client: HTTP client for making requests.
        url: URL of the page to fetch.
    Returns:
        List of forum objects.
    """
    url = base_url.format(page=page)
    async with sem:
        res = await client.get(url)
        res.raise_for_status()
        data = res.json()
        forums = data.get("pageProps", {}).get("forums", [])
        return [extract_forum_info(f) for f in forums]


async def scrape_forum_page(params: dict) -> list[dict]:
    base_url = params.get("base_url")
    if not base_url:
        raise ValueError("Base URL is required.")

    concurrent_limit = params.get("concurrent_limit", 3)
    timeout_sec = params.get("timeout", 20)
    headers = params.get("headers", {})
    if not isinstance(headers, dict):
        logger.warning("Invalid headers, using empty dict.")
        headers = {}

    sem = asyncio.Semaphore(concurrent_limit)
    timeout = httpx.Timeout(timeout_sec)

    # sem = asyncio.Semaphore(params["concurrent_limit"])
    # timeout = httpx.Timeout(params["timeout"])
    # base_url = params["base_url"]
    # headers = params["headers"]

    async with httpx.AsyncClient(timeout=timeout, headers=headers) as client:
        page_end = await get_total_pages(client, base_url)
        tasks = [
            fetch_forum_page(client=client, page=page, sem=sem, base_url=base_url)
            for page in range(1, page_end + 1)
        ]
        results = await tqdm_asyncio.gather(*tasks)
        return [forum for sublist in results for forum in sublist]


def run_scraping_pipeline(params: dict) -> list[dict]:
    return asyncio.run(scrape_forum_page(params))
