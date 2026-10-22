import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from urllib.parse import urlsplit, urlunsplit

import streamlit as st
from dotenv import load_dotenv
from tavily import TavilyClient


load_dotenv()


def clean_url(url: str) -> str:
    parts = urlsplit(url)

    return urlunsplit(
        (
            parts.scheme,
            parts.netloc,
            parts.path.rstrip("/"),
            "",
            ""
        )
    )


def search_one_query(category: str, query: str) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")

    tavily_client = TavilyClient(api_key=api_key)

    response = tavily_client.search(
        query=query,
        search_depth="basic",
        max_results=2,
        include_answer=False
    )

    results = []

    for result in response.get("results", []):
        url = result.get("url", "")

        if not url:
            continue

        results.append(
            {
                "query": query,
                "category": category,
                "title": result.get(
                    "title",
                    "Untitled result"
                ),
                "url": url,
                "content": result.get(
                    "content",
                    "No preview available."
                )
            }
        )

    return results


@st.cache_data(ttl=3600, show_spinner=False)
def search_public_web(search_queries: dict) -> list[dict]:
    api_key = os.getenv("TAVILY_API_KEY")

    if not api_key:
        raise ValueError(
            "TAVILY_API_KEY was not found."
        )

    tasks = []

    query_categories = [
        "title_queries",
        "project_queries",
        "skill_queries",
        "company_queries",
        "broader_queries"
    ]

    for category in query_categories:
        queries = search_queries.get(category, [])

        for query in queries:
            tasks.append((category, query))

    all_results = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        future_tasks = {
            executor.submit(
                search_one_query,
                category,
                query
            ): (category, query)
            for category, query in tasks
        }

        for future in as_completed(future_tasks):
            try:
                results = future.result()
                all_results.extend(results)
            except Exception:
                continue

    unique_results = []
    seen_urls = set()

    for result in all_results:
        normalized_url = clean_url(result["url"])

        if normalized_url in seen_urls:
            continue

        seen_urls.add(normalized_url)
        unique_results.append(result)

    return unique_results