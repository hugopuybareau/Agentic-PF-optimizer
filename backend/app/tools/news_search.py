# backend/app/services/news_search.py

import requests
import os

from typing import List, Dict, Optional
# from langchain_community.tools.bing_search.tool import BingSearchResults
# from langchain.tools import Tool

class NewsSearchTool:
    def __init__(self):
        self.api_key = os.getenv('NEWS_SEARCH_API_KEY')
        self.endpoint = "https://newsapi.org/v2/everything"

    def search(
        self, 
        query: str, 
        from_date: Optional[str] = None, 
        to_date: Optional[str] = None, 
        language: str = "en", 
        page_size: int = 10
    ) -> List[Dict]:
        params = {
            "q": query,
            "language": language,
            "pageSize": page_size,
            "apiKey": self.api_key
        }
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date

        response = requests.get(self.endpoint, params=params)
        response.raise_for_status()
        articles = response.json().get("articles", [])

        return articles


# def search_news(query: str, num_results: int = 5):
#     """
#     Search for recent news using Bing Search API.
    
#     Args:
#         query (str): The search query (e.g. "Tesla earnings 2024").
#         num_results (int): Number of results to return.
        
#     Returns:
#         List[dict]: List of news results with title, url, snippet.
#     """
#     bing = BingSearchResults()
#     results = bing.run(query, num_results=num_results)
#     # results is a list of dicts with keys: 'title', 'snippet', 'link'
#     return results