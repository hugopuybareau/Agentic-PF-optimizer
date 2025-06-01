# backend/app/services/news.py

from langchain_community.tools.bing_search.tool import BingSearchResults
from langchain.tools import Tool

import os

# Set your Bing Search API key as an environment variable for security
os.environ["BING_SEARCH_URL"] = "https://api.bing.microsoft.com/v7.0/search"
os.environ["BING_SUBSCRIPTION_KEY"] = "<YOUR_BING_API_KEY>"

def search_news(query: str, num_results: int = 5):
    """
    Search for recent news using Bing Search API.
    
    Args:
        query (str): The search query (e.g. "Tesla earnings 2024").
        num_results (int): Number of results to return.
        
    Returns:
        List[dict]: List of news results with title, url, snippet.
    """
    bing = BingSearchResults()
    results = bing.run(query, num_results=num_results)
    # results is a list of dicts with keys: 'title', 'snippet', 'link'
    return results

# Example usage:
if __name__ == "__main__":
    news = search_news("Apple Inc. latest news 2024", num_results=3)
    for idx, item in enumerate(news, 1):
        print(f"{idx}. {item['title']}\n{item['link']}\n{item['snippet']}\n")
