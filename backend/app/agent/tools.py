# backend/app/agent/tools.py

import os

from langchain_community.tools.bing_search.tool import BingSearchResults
from langchain.tools import Tool

BING_SUBSCRIPTION_KEY = os.getenv("BING_SUBSCRIPTION_KEY")
BING_SEARCH_URL = os.getenv("BING_SEARCH_ENDPOINT")

def search_news(query: str, num_results: int = 5):
    bing = BingSearchResults()
    results = bing.run(query, num_results=num_results)
    return results

