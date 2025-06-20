# App Concept

---

## Conversational Agent for Portfolio (PF) Setup & Optimization

- Define/Upload a portfolio  
  *e.g. “I have 15 AAPL shares, 1 BTC, and a mortgage on my house”*
- Ask questions  
  *e.g. “How risky is my portfolio?” “Should I diversify more?”*
- Get recommendations  
  *e.g. “What would you add to reduce risk?”*

**The agent should be able to:**
- Retrieve portfolio state/history for the user.
- Access relevant recent news, analysis, and knowledge.
- Reason with both up-to-date and persistent information.
- Take actions  
  *e.g. “add/remove asset”, “rebalance suggestion”, etc.*

---

## Ongoing Monitoring & Push Alerts

Once set up, the agent:
- Watches for relevant news/market changes.
- Summarizes and sends updates/alerts (daily digest, risk events, suggestions).
- Delivers insights via chat, dashboard, or notifications.

---

## Agentic Architecture & Tools

- **Agent Orchestrator:**  
  Receives user input or scheduled task, decides which tools to invoke and how to compose the final answer/digest.

- **Vector Database Tool:**  
  - **Stores** all fetched articles, news, analyses, and chat history.
  - **Enables semantic search** (“show me recent bearish news about my assets”).
  - **Provides memory** so the agent can retrieve context without redundant external API calls.
  - **Supports RAG** (Retrieval-Augmented Generation) for more grounded and relevant LLM outputs.

- **Search News Tool:**  
  - Fetches latest news from web APIs (Bing, Google News, etc.)  
  - Only called if the vector DB does not have sufficient/recent info.

- **Classify Tool:**  
  - Tags news by sentiment, impact, relevance, risk type, and quality.
  - Filters out noise and enables intelligent summarization/alerting.

- **Summarize Tool:**  
  - Synthesizes key findings and produces concise updates.
  - Can summarize by asset, by category, or portfolio-wide.

---

## Example Workflow

1. **User (via chat or dashboard) interacts with agent:**
    - “Show me important news about my portfolio.”
2. **Agent orchestrator:**
    - Searches vector DB for relevant, recent articles about each asset.
    - If not enough info, calls the Search News Tool and stores new results in vector DB.
    - Classifies news items (sentiment, impact, etc.).
    - Summarizes findings for user.
    - Optionally, updates portfolio state or sends proactive recommendations/alerts.

---

## Benefits

- **Cheaper, faster**: fewer external API calls.
- **Smarter agent**: leverages memory and context for better answers.
- **User-friendly**: delivers actionable, timely, and relevant advice via chat or notification.

---

## Future-proof & Extensible

- Easily add new asset types, data sources, or analysis tools.
- Scalable to large portfolios or multiple users.
- Enables powerful user queries and longitudinal analysis (“show all negative news on my portfolio in the last 6 months”).

---
