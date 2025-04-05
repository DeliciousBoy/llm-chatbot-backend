import asyncio

import httpx

BASE_URL = "https://www.agnoshealth.com/_next/data/i499vlSTx42EOnWUOHBkP/th/forums/search.json?page={page}"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/134.0.0.0 Safari/537.36 Edg/134.0.0.0"
    )
}

TIMEOUT = httpx.Timeout(20.0)
CONCURRENT_LIMIT = 3


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


async def fetch_page(
    *, client: httpx.AsyncClient, page: int, sem: asyncio.Semaphore
) -> list[dict]:
    """Fetches a page of forum data.

    Args:
        client: HTTP client for making requests.
        url: URL of the page to fetch.
    Returns:
        List of forum objects.
    """
    url = BASE_URL.format(page=page)
    async with sem:
        try:
            res = await client.get(url)
            res.raise_for_status()
            data = res.json()
            forums = data.get("pageProps", {}).get("forums", [])
            return [extract_forum_info(f) for f in forums]
        except Exception as e:
            print(f"Error fetching page {page}: {e}")
            return []


async def scrape_all_pages() -> list[dict]:
    sem = asyncio.Semaphore(CONCURRENT_LIMIT)
    async with httpx.AsyncClient(timeout=TIMEOUT, headers=HEADERS) as client:
        tasks = [
            fetch_page(client=client, page=page, sem=sem) for page in range(1, 178)
        ]
        results = await asyncio.gather(*tasks)
        return [forum for sublist in results for forum in sublist]


def test() -> list[dict]:
    import asyncio

    return asyncio.run(scrape_all_pages())
