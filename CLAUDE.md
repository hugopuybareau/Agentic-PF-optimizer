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

### Data Models (backend/app/models/)
- **Centralized Model Architecture**: All Pydantic models consolidated in `/models/` folder with complete type safety
- **Core Models**:
  - `assets.py`: Asset types (Stock, Crypto, RealEstate, Mortgage, Cash) with `AssetType` literal for type safety
  - `portfolio.py`: Portfolio and PortfolioRequest models
  - `chat.py`: ChatMessage, ChatSession, PortfolioBuildingState for conversational workflows
  - `agent_state.py`: ChatAgentState, AgentState for LangGraph workflow states
  - `analysis.py`: AnalysisResult, NewsItem for portfolio analysis
  - `responses.py`: All LLM response models (Intent, EntityData, UIHints, etc.)
  - `portfolio_responses.py`: Portfolio action models (AssetConfirmation, PortfolioConfirmationRequest, etc.)
  - `portfolio_requests.py`: Portfolio modification request models
- **Type Safety**: All asset types use `AssetType` literal instead of strings for compile-time validation
- **Clean Imports**: All models accessible via `from app.models import ModelName`

### Chat Agent System (backend/app/agents/)
- **ChatAgent** (`chat_agent.py`): Conversational agent for building portfolios through natural language
  - Uses Azure OpenAI GPT-4o-mini for intent classification and entity extraction
  - **LangGraph Workflow**: classify_intent → extract_entities → prepare_confirmation → update_portfolio → generate_response/prepare_form
  - **Portfolio Modification Tools**: Handles add_asset, remove_asset, modify_asset with user confirmation flows
  - **Confirmation System**: Two-step process - conversation builds portfolio in-memory, confirmation updates database
  - Handles progressive asset collection and context-aware references
- **Session Management** (`session_storage.py`): Redis-backed session storage with in-memory fallback
  - Supports Redis for production, hybrid mode for development
  - TTL-based session expiration and cleanup
- **Modular Architecture**: Separate modules for intent classification, entity extraction, portfolio operations, response generation

### Portfolio Analysis Agent
- **PortfolioAgent** (`portfolio_agent.py`): LangGraph workflow for portfolio analysis and market insights
- **Tools** (`tools.py`): NewsSearchTool, ClassificationTool, AnalysisTool, PortfolioSummarizerTool
- **Vector Store** (`core/vector_store.py`): Qdrant integration for semantic search and news storage

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
- **Portfolio Modification Tools**: Complete CRUD operations for portfolio assets
  - Add assets through natural conversation ("I want to add 100 shares of Apple")
  - Remove assets ("Remove my Tesla position")
  - Modify existing assets ("Update my Apple shares to 150")
  - Complete portfolio building workflow
- **Two-Phase Portfolio Management**:
  - **Phase 1**: Conversational building - assets stored in in-memory session state
  - **Phase 2**: Database persistence - user confirms actions before database updates
- **Streaming Chat Output**: Real-time message streaming for responsive user experience
- **Intent Classification**: Handles add_asset, remove_asset, modify_asset, complete_portfolio, view_portfolio, etc.
- **Entity Extraction**: Extracts asset details (ticker, amount, type) from natural language with `AssetType` validation
- **Context Awareness**: Resolves references like "the same amount", "that stock"
- **Confirmation System**: User-friendly confirmation dialogs for all portfolio modifications
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

### Model Architecture
- **Centralized Models**: All data models located in `backend/app/models/` for single source of truth
- **Domain Separation**: Models organized by domain (assets, chat, analysis, responses, portfolio_responses) not by location
- **Clean Imports**: Use `from app.models import Model` instead of deep imports
- **Type Safety**: Complete Pydantic model usage throughout - no dict access patterns
  - All agent methods use proper Pydantic models and enum types (e.g., `Intent` enum not strings)
  - `AssetType` literal ensures compile-time validation of asset types
  - LangGraph nodes return `ChatAgentState` objects using `state.model_copy(update={...})` pattern
  - All state access uses Pydantic attributes (`state.field`) not dict access (`state["field"]`)
- **Professional Patterns**: Immutable state updates with proper type checking

### Agent Development
- **LangGraph Architecture**: Both agents use LangGraph StateGraph for workflow orchestration
- **Pure Pydantic Models**: All state classes use Pydantic BaseModel (no TypedDict) for complete type safety
  - Nodes return `ChatAgentState` objects using `state.model_copy(update={...})` pattern
  - No dict access anywhere - only `state.attribute` access patterns
  - Complete type checking and IntelliSense support
- **Modular Tools**: Portfolio operations, entity extraction, response generation are separate modules
- **Portfolio Workflow**: 
  - In-memory portfolio building during conversation
  - Confirmation-based database persistence
  - Support for complex multi-asset operations
- **Error Handling**: Graceful fallbacks and user-friendly messages
- **Structured Output**: All LLM calls use Pydantic models with proper schemas for OpenAI compatibility
- **Type Safety**: Methods return proper types (Intent enum, AssetType literal) not mixed string/enum types

### Session Management
- Use `get_session_storage()` factory for environment-appropriate storage
- Sessions auto-expire (default 60 minutes TTL)
- Chat state includes portfolio building progress and conversation history
- Handle Redis connection failures gracefully with in-memory fallback

### Testing
- Backend tests in `backend/test/` directory
- Test both individual tools and full agent workflows
- Mock external API calls (Azure OpenAI, NewsAPI)

### Portfolio Modification System
- **Dual-Phase Architecture**:
  - **Session State**: In-memory portfolio building during chat conversation
  - **Database State**: Persistent storage after user confirmation
- **Confirmation Workflow**:
  - User expresses intent ("Add 100 AAPL shares")
  - System extracts entities and prepares confirmation
  - User confirms/rejects the action
  - Database updated only after confirmation
- **Portfolio Operations** (`agents/modules/portfolio_operations.py`):
  - Handles in-memory portfolio state updates
  - Creates Asset objects from extracted entities
  - Manages UI hints for frontend guidance
- **Portfolio Service** (`agents/services/portfolio_service.py`):
  - Database operations for confirmed portfolio changes
  - CRUD operations on persistent portfolio data
  - Portfolio summary and validation

## Commit Conventions
Follow format: `<type>(optional-scope): <short summary>`
Types: feat, fix, docs, style, refactor, perf, test, build, chore