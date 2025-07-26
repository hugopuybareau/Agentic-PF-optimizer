# 🤖 Agentic Portfolio Optimizer

*An intelligent conversational AI platform for portfolio analysis and optimization*

---

## 🌟 Overview

Agentic Portfolio Optimizer is a sophisticated AI-powered platform that combines conversational portfolio building with advanced financial analysis. Using dual LangGraph agents and modern web technologies, it provides an intuitive way to build, analyze, and optimize investment portfolios through natural language interactions.

## ✨ Key Features

### 🗣️ **Conversational Portfolio Building**
- **Natural Language Input**: Build your portfolio by simply describing your assets
- **Progressive Collection**: Smart entity extraction and context-aware follow-up questions
- **Real-time Validation**: Instant feedback and error handling during portfolio creation
- **Multi-Asset Support**: Stocks, crypto, real estate, mortgages, and cash positions

### 🧠 **AI-Powered Analysis**
- **Dual Agent Architecture**: Specialized ChatAgent for building + PortfolioAgent for analysis
- **Automated News Integration**: Fetches and classifies relevant market news
- **Risk Assessment**: Comprehensive portfolio risk analysis and recommendations
- **Semantic Search**: Vector database for intelligent content retrieval and context

### 🎨 **Modern User Experience**
- **Glassmorphism Design**: Beautiful overlay modals with backdrop blur effects
- **Responsive Interface**: Optimized for desktop and mobile devices
- **Dark/Light Themes**: Seamless theme switching with system preference detection
- **Internationalization**: Full support for English and French languages

### 🔧 **Technical Excellence**
- **Real-time Sessions**: Redis-backed chat sessions with automatic expiration
- **Type Safety**: Full TypeScript implementation with comprehensive error handling
- **Containerized Deployment**: Docker-compose setup for easy development and production
- **API Documentation**: FastAPI with automatic OpenAPI documentation

## 🏗️ Architecture

```
┌─────────────────┬─────────────────┬─────────────────┐
│   Frontend      │    Backend      │   Data Layer    │
│   (React)       │   (FastAPI)     │                 │
├─────────────────┼─────────────────┼─────────────────┤
│ • React 18      │ • FastAPI       │ • PostgreSQL    │
│ • TypeScript    │ • Python 3.13   │ • Qdrant (Vector)│
│ • Tailwind CSS │ • LangGraph     │ • Redis (Cache) │
│ • Vite          │ • Azure OpenAI  │                 │
│ • shadcn/ui     │ • uv (pkg mgr)  │                 │
└─────────────────┴─────────────────┴─────────────────┘
```

### 🤖 **Agent System**
- **ChatAgent**: Handles conversational portfolio building with intent classification and entity extraction
- **PortfolioAgent**: Performs market analysis, news classification, and generates insights
- **Session Storage**: Hybrid Redis/in-memory storage with automatic fallback
- **Vector Store**: Qdrant integration for semantic search and news storage

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+**
- **uv** (Python package manager) - [Install uv](https://docs.astral.sh/uv/getting-started/installation/)
- **Node.js 18+**
- **Docker Desktop** (recommended)
- **Azure OpenAI API Key** (for chat functionality)
- **NewsAPI Key** (optional, for news search)

### 🐳 Docker Setup (Recommended)

1. **Clone the repository**
```bash
git clone https://github.com/hugopuybareau/Agentic-PF-optimizer.git
cd Agentic-PF-optimizer
```

2. **Configure environment**
```bash
# Create .env file with your API keys
cp .env.example .env
# Edit .env with your Azure OpenAI and other credentials
```

3. **Start all services**
```bash
# Build and start all containers
./build.sh

# Or manually with docker-compose
docker-compose up -d
```

4. **Access the application**
- **Frontend**: http://localhost:8080
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 💻 Local Development Setup

#### Backend (with uv)
```bash
cd backend

# Install uv if not already installed
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment with uv
uv venv .venv

# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies with uv
uv pip install -r requirements.txt

# Start development server
uvicorn app.main:app --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
```

#### Services (Optional)
```bash
# Start only databases
docker-compose up -d postgres qdrant redis
```

## 📊 Service Ports

| Service    | Port | Description                    |
|------------|------|--------------------------------|
| Frontend   | 8080 | React development server       |
| Backend    | 8000 | FastAPI application            |
| PostgreSQL | 55432| User data and portfolios       |
| Qdrant     | 6333 | Vector database for news/analysis |
| Redis      | 6379 | Session storage and caching    |

## 🛠️ Development Commands

### Backend (with uv)
```bash
# Start development server
uvicorn app.main:app --reload

# Install new package
uv add package-name

# Install dev dependencies
uv add --dev package-name

# Update dependencies
uv pip compile requirements.in -o requirements.txt

# Run tests
python -m pytest test/

# Format code
ruff format .
ruff check .
```

### Frontend
```bash
# Development server
npm run dev

# Build for production
npm run build

# Build for development
npm run build:dev

# Lint code
npm run lint
```

### Docker
```bash
# Build and start with logs
./build.sh

# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## 🌐 API Endpoints

### Chat System
- `POST /api/chat/message` - Send chat messages for portfolio building
- `POST /api/chat/submit-portfolio` - Submit built portfolio for analysis
- `GET /api/chat/session/{id}/portfolio` - Get session portfolio state
- `DELETE /api/chat/session/{id}` - Clear chat session
- `GET /api/chat/suggestions` - Get asset suggestions and templates

### Portfolio Analysis
- `POST /api/digest` - Generate portfolio analysis report
- `POST /api/analyze` - Perform detailed portfolio analysis
- `GET /api/alerts` - Get portfolio risk alerts

### Authentication
- `POST /api/auth/register` - Create new user account
- `POST /api/auth/login` - User authentication
- `GET /api/auth/me` - Get current user profile

## 🎯 Asset Types Supported

| Type | Examples | Fields |
|------|----------|---------|
| **Stocks** | AAPL, MSFT, GOOGL | ticker, shares |
| **Crypto** | BTC, ETH, SOL | symbol, amount |
| **Real Estate** | Primary residence, rental | address, market_value |
| **Mortgages** | Home loans | lender, balance, property_address |
| **Cash** | Savings, checking | currency, amount |

## 🧪 Testing

```bash
# Backend tests
cd backend
python -m pytest test/ -v

# Frontend tests (if available)
cd frontend
npm test
```

## 📝 Contributing

We welcome contributions! Please follow these guidelines:

### Branch Strategy
- `main` - Production ready code
- `feature/feature-name` - New features
- `fix/bug-description` - Bug fixes

### Commit Convention
```
<type>(scope): <description>

Types: feat, fix, docs, style, refactor, perf, test, build, chore
```

### Development Process
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## 📚 Documentation

- **API Documentation**: Available at `/docs` when running the backend
- **Development Guide**: See `CLAUDE.md` for detailed development instructions
- **Architecture Details**: Check the `MDs/concept.MD` for system design

## 🔒 Security

- JWT-based authentication
- Input validation and sanitization
- SQL injection protection via SQLAlchemy
- CORS configuration for secure cross-origin requests
- Environment variable management for sensitive data

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Acknowledgments

- **LangChain/LangGraph** for agent orchestration
- **FastAPI** for the robust backend framework
- **Qdrant** for vector database capabilities
- **shadcn/ui** for beautiful UI components
- **Azure OpenAI** for conversational AI capabilities
- **uv** for fast Python package management

---

*Built with ❤️ for intelligent portfolio management*