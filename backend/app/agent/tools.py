# backend/app/agent/tools.py

from langchain_community.tools.bing_search.tool import BingSearchResults
from langchain.tools import Tool

from ..secrets import get_secrets

secrets = get_secrets()
BING_SUBSCRIPTION_KEY = secrets["BING_SUBSCRIPTION_KEY"]
BING_SEARCH_URL = secrets["BING_SEARCH_ENDPOINT"]

def search_news(query: str, num_results: int = 5):
    bing = BingSearchResults()
    results = bing.run(query, num_results=num_results)
    return results

