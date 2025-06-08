# Agentic Portfolio Optimizer

--------------

A conversational AI agent that helps you define, analyze, and optimize your financial portfolio.  
Built with FastAPI (Python backend), a vector database, and containerized for easy deployment.

## Features

- **Conversational Portfolio Setup**: Define or upload your portfolio using natural language.
- **Intelligent Q&A**: Ask questions about your portfolio risk, diversification, and get actionable recommendations.
- **Automated News & Analysis**: Fetches, classifies, and summarizes relevant news to monitor your assets.
- **Ongoing Monitoring & Alerts**: Get daily digests, risk alerts, and optimization tips delivered via chat or dashboard.
- **Extensible & Modular**: Easily plug in new asset types, data sources, or analysis tools.

## Project Structure

/backend # FastAPI backend code (including app/, requirements.txt, etc.)  
/frontend  
/docker-compose.yml  
/backend/Dockerfile  

## Quickstart (Dev)

### Prerequisites

- Python 3.13+
- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (recommended)
- [NewsAPI API Key](https://newsapi.org/) (for testing news search)

### Local Setup (without Docker)

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Contributing

Feature branches: feature/<feature-name>
Pull requests required for all changes to main
Keep backend and frontend as separate services/images
