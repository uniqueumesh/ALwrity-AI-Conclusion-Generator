from __future__ import annotations

import os
import json
import requests


def get_serp_competitor_snippets(search_query: str, user_serper_api_key: str | None = None):
    serper_api_key = user_serper_api_key or os.getenv('SERPER_API_KEY')
    if not serper_api_key:
        return []

    url = "https://google.serper.dev/search"
    payload = json.dumps({
        "q": search_query,
        "gl": "us",
        "hl": "en",
        "num": 10,
        "autocorrect": True,
        "page": 1,
        "type": "search",
        "engine": "google",
    })
    headers = {
        'X-API-KEY': serper_api_key,
        'Content-Type': 'application/json',
    }
    try:
        response = requests.post(url, headers=headers, data=payload, timeout=30)
        if response.status_code == 429 or 'rate limit' in response.text.lower() or 'quota' in response.text.lower():
            return 'RATE_LIMIT'
        if response.status_code == 200:
            data = response.json()
            snippets = []
            for item in data.get('organic', [])[:10]:
                title = item.get('title')
                snippet = item.get('snippet')
                if title and snippet:
                    snippets.append(f"{title} — {snippet}")
                elif title:
                    snippets.append(title)
            return snippets
        return []
    except Exception:
        return []


