# backend/test/news_search_tool.py

import json

from ..app.tools.news_search import NewsSearchTool

def test_news_search():
    tool = NewsSearchTool()
    results = tool.search("Bitcoin", page_size=3)
    assert isinstance(results, list)
    assert len(results) > 0
    print(json.dumps(results, indent=4, ensure_ascii=False))

if __name__ == "__main__":
    test_news_search()