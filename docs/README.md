# CodeMentor AI

An AI-powered technical interview preparation platform that provides personalized feedback on coding solutions. The system executes code, analyzes structure, estimates complexity, and generates detailed improvement suggestions using GPT-5.

## Live Demo

**Try it now:** [http://your-deployment-url.com](http://your-deployment-url.com)

## Demo Video

[Video will be embedded here - 90 seconds]

## Features

- **Code Execution Engine**: Isolated Python code execution with timeout and resource limits
- **Static Code Analysis**: AST-based parsing to detect loops, recursion, data structures, and code patterns
- **Complexity Estimation**: Automatic time and space complexity analysis with optimal comparison
- **AI-Powered Feedback**: GPT-5 generates personalized code reviews with specific improvement suggestions
- **Multi-Language Support**: Python support (JavaScript ready to implement)
- **Progress Tracking**: Dashboard showing problems solved and performance metrics
- **Test Case Validation**: Visible and hidden test cases for comprehensive solution validation

## Tech Stack

### Frontend
- React 18
- TailwindCSS
- Vite

### Backend
- FastAPI (Python 3.11)
- PostgreSQL 15
- SQLAlchemy 2.0 (async)
- Alembic (migrations)
- Redis (caching and sessions)

### AI Integration
- **Primary**: Azure OpenAI GPT-5
- **Models**: gpt-5-chat deployment
- **Features**: Code analysis, feedback generation, error classification

### Deployment
- Backend: Docker + Docker Compose
- Database: PostgreSQL (containerized)
- Cache: Redis (containerized)

## Setup Instructions

### Prerequisites
- Docker and Docker Compose
- Python 3.11+
- Node.js 18+
- Azure OpenAI API access

### Installation

```bash
# Clone the repository
git clone https://github.com/your-team/codementor-ai.git
cd codementor-ai

# Backend Setup
cd backend
cp .env.example .env
# Edit .env with your API keys

# Start services with Docker
docker-compose up -d

# Run migrations
docker exec -it codementor_backend alembic upgrade head

# Seed problems
docker exec -it codementor_backend python -m scripts.seed_problems

# Frontend Setup
cd ../frontend
npm install
npm run dev
```

The application will be available at:
- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8001`
- API Docs: `http://localhost:8001/docs`

## Environment Variables

See `.env.example` for all required variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://codementor:codementor_pass@postgres:5432/codementor_db
DATABASE_URL_SYNC=postgresql://codementor:codementor_pass@postgres:5432/codementor_db

# Redis
REDIS_URL=redis://redis:6379/0

# Azure OpenAI
AZURE_OPENAI_API_KEY=your_key_here
AZURE_OPENAI_ENDPOINT=https://your-endpoint.cognitiveservices.azure.com/
AZURE_OPENAI_API_VERSION=2025-01-01-preview
AZURE_OPENAI_DEPLOYMENT=gpt-5-chat

# Application
SECRET_KEY=your_secure_secret_here
CODE_EXECUTION_TIMEOUT=10
```

## Usage Examples

### 1. Register and Login
Create an account and authenticate to access the platform.

### 2. Select a Problem
Choose from 5 curated coding problems (Two Sum, Valid Parentheses, etc.)

### 3. Write and Submit Code
Use the integrated code editor to write your solution and submit for analysis.

### 4. Receive AI Feedback
Get detailed feedback including:
- Test results (pass/fail for each case)
- Code structure analysis (loops, data structures, patterns)
- Complexity estimation (time and space)
- Personalized improvement suggestions from GPT-5
- Specific recommendations on what to improve

## System Architecture

```
User → React Frontend
    ↓
FastAPI Backend
    ↓
┌─────────────┬─────────────┬─────────────┐
│  Execution  │    AST      │ Complexity  │
│   Service   │  Analyzer   │  Analyzer   │
└─────────────┴─────────────┴─────────────┘
                    ↓
            Azure OpenAI GPT-5
            (Feedback Generation)
                    ↓
            PostgreSQL Database
```

## Team

 - Mariam Khokhiashvili(@MariamKhoKh)
 - Tinatin Javakhadze(@tjavakhadze)
 - Gvantsa Tchuradze(@Gvantsa21)
 - Davit Karoiani(@D13Karo)

## Documentation

- [Architecture Overview](docs/ARCHITECTURE.md)
- [Case Study](docs/CASE_STUDY.md)
- [Deployment Guide](docs/DEPLOYMENT.md)
- [API Documentation](docs/API.md)

## License

MIT License - see LICENSE file

## Acknowledgments

- Professor Zeshan Ahmad
- Kutaisi International University
- Building AI-Powered Applications Course (CS-AI-2025)