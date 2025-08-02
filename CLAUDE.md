# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Backend (Python/FastAPI with uv)
- **Setup environment**: `cd backend && uv venv .venv && source .venv/bin/activate`
- **Install dependencies**: `uv pip install -r requirements.txt`
- **Start backend**: `uvicorn app.main:app --reload` (dev mode)
- **Add new package**: `uv add package-name` or `uv add --dev package-name`
- **Lint Python code**: `ruff check .` and `ruff format .` (use pyproject.toml config)
- **Run backend tests**: `python -m pytest test/`

### Frontend (React/Vite)
- **Start frontend**: `cd frontend && npm run dev` (runs on default Vite port)
- **Install dependencies**: `cd frontend && npm install`
- **Build frontend**: `npm run build` (production) or `npm run build:dev` (development)
- **Lint frontend**: `cd frontend && npm run lint`

### Full Application (Docker)
- **Build and run all services**: `./build.sh` (builds containers and starts with logs)
- **Start services**: `docker-compose up -d`
- **View logs**: `docker-compose logs -f`
- **Stop services**: `docker-compose down`

## Architecture Overview

### Core Components
- **Backend**: FastAPI app with dual agent system - ChatAgent for conversational portfolio building and PortfolioAgent for analysis
- **Frontend**: React SPA with shadcn/ui components, TypeScript, Tailwind CSS, and React Router
- **Databases**: PostgreSQL (user data, portfolios), Qdrant vector database (news/analysis storage), Redis (chat session storage)
- **Agent System**: Two LangGraph workflows - chat flow for portfolio building and analysis flow for market insights

### Chat Agent System (backend/app/agents/)
- **ChatAgent** (`chat_agent.py`): Conversational agent for building portfolios through natural language
  - Uses Azure OpenAI GPT-4o-mini for intent classification and entity extraction
  - LangGraph workflow: classify_intent → extract_entities → update_portfolio → generate_response/prepare_form
  - Handles progressive asset collection and context-aware references
- **Session Management** (`session_storage.py`): Redis-backed session storage with in-memory fallback
  - Supports Redis for production, hybrid mode for development
  - TTL-based session expiration and cleanup
- **State Models** (`state/chat_state.py`): Pydantic models for chat sessions and portfolio building state

### Portfolio Analysis Agent
- **PortfolioAgent** (`portfolio_agent.py`): LangGraph workflow for portfolio analysis and market insights
- **State Management** (`state/agent.py`, `state/analysis.py`): Defines analysis workflow state
- **Tools** (`tools.py`): NewsSearchTool, ClassificationTool, AnalysisTool, PortfolioSummarizerTool
- **Vector Store** (`vector_store.py`): Qdrant integration for semantic search and news storage

### API Structure
- **Chat System**: `/api/chat/*` 
  - `POST /api/chat/message` - Send chat messages for portfolio building
  - `POST /api/chat/message/stream` - Streaming chat messages with real-time responses
  - `GET /api/chat/session/{session_id}` - Get full session data including messages and portfolio
  - `GET /api/chat/session/{session_id}/portfolio` - Get session portfolio state
  - `DELETE /api/chat/session/{session_id}` - Clear chat session
  - `GET /api/chat/suggestions` - Get asset suggestions and templates
- **Authentication**: `/api/auth/*` (JWT-based, see `routers/auth.py`)
- **Portfolio Analysis**: `/api/digest`, `/api/analyze`, `/api/alerts` (see `routers/digest.py`)
- **Models**: Asset types (stock, crypto, real_estate, mortgage, cash) in `models/assets.py`

### Frontend Structure
- **Routing**: React Router with pages in `src/pages/` (Landing, Chat, Portfolio, Alerts, etc.)
- **UI Components**: shadcn/ui system in `src/components/ui/`
- **State Management**: React Query for server state, context for auth
- **Internationalization**: i18next with English/French translations
- **Theming**: Dark/light mode with next-themes

## Development Setup

### Environment Requirements
- Python 3.13+ (backend uses Python 3.13 features)
- **uv** (Python package manager) - faster than pip, used throughout the project
- Node.js for frontend
- Docker Desktop for full stack development
- Azure OpenAI API key for chat functionality
- NewsAPI key for news search functionality
- Redis for session storage (production) or runs in-memory (development)

### Container Services & Ports
- Frontend: 8080
- Backend: 8000  
- PostgreSQL: 55432 (mapped from 5432)
- Qdrant: 6333
- Redis: 6379

### Key Configuration Files
- `pyproject.toml`: Python code formatting (Black, Ruff with line length 100)
- `docker-compose.yml`: Multi-service setup with Redis, volume mounts for development
- `frontend/package.json`: Vite build system with TypeScript and ESLint
- `.env`: Environment variables for API keys and database connections

### Chat System Features
- **Conversational Portfolio Building**: Natural language asset collection with progressive questioning
- **Streaming Chat Output**: Real-time message streaming for responsive user experience
- **Intent Classification**: Handles add_asset, remove_asset, modify_asset, complete_portfolio, etc.
- **Entity Extraction**: Extracts asset details (ticker, amount, type) from natural language
- **Context Awareness**: Resolves references like "the same amount", "that stock"
- **Session Persistence**: Redis-backed sessions with automatic expiration and cross-tab restoration
- **Tab-Aware Session Restoration**: Sessions persist when switching browser tabs and automatically restore chat history
- **Form Generation**: Converts chat-built portfolio to structured form for review
- **Asset Suggestions**: Provides common stocks, cryptos, and portfolio templates

#### Session Management
- **Backend Storage**: Sessions stored in Redis with chat messages and portfolio building state
- **Frontend Persistence**: Session ID stored in localStorage for cross-tab continuity
- **Automatic Restoration**: When returning to chat tab, full session including messages is restored from backend
- **Visibility API Integration**: Uses browser visibility API to detect tab changes and trigger restoration
- **Graceful Degradation**: Falls back to in-memory storage if Redis unavailable

## Development Patterns

### Feature Development Guidelines
- **Translation Keys**: When adding new features with user-facing text, ALWAYS update translation keys in both English and French files (`frontend/public/locales/`)
- **Internationalization**: Ensure all new UI text uses i18next translation keys instead of hardcoded strings
- **Feature Integration**: For significant new features, update this CLAUDE.md file to document the integration

### Agent Development
- Both agents use LangGraph StateGraph for workflow orchestration
- State classes use TypedDict for type safety and Pydantic for validation
- Tools are modular and can be easily extended or replaced
- Error handling with graceful fallbacks and user-friendly messages

### Session Management
- Use `get_session_storage()` factory for environment-appropriate storage
- Sessions auto-expire (default 60 minutes TTL)
- Chat state includes portfolio building progress and conversation history
- Handle Redis connection failures gracefully with in-memory fallback

### Testing
- Backend tests in `backend/test/` directory
- Test both individual tools and full agent workflows
- Mock external API calls (Azure OpenAI, NewsAPI)

## Commit Conventions
Follow format: `<type>(optional-scope): <short summary>`
Types: feat, fix, docs, style, refactor, perf, test, build, chore