# System Architecture

## High-Level Overview

CodeMentor AI is a full-stack web application that combines code execution, static analysis, and AI-powered feedback to help users prepare for technical interviews.

## Architecture Diagram

```
┌─────────────────┐
│   React         │
│   Frontend      │
│   (Port 5173)   │
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│   FastAPI       │
│   Backend       │
│   (Port 8001)   │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬───────────┐
    ▼         ▼          ▼           ▼
┌────────┐ ┌────────┐ ┌─────────┐ ┌─────────┐
│Execute │ │  AST   │ │Complexity│ │Azure    │
│Service │ │Analyzer│ │Analyzer  │ │OpenAI   │
└────────┘ └────────┘ └─────────┘ └─────────┘
                                       │
                                       ▼
                               ┌─────────────┐
                               │   GPT-5     │
                               │  Feedback   │
                               └─────────────┘
    ┌────────────────┬──────────────┐
    ▼                ▼              ▼
┌──────────┐   ┌──────────┐   ┌──────────┐
│PostgreSQL│   │  Redis   │   │  Docker  │
│ Database │   │  Cache   │   │Containers│
└──────────┘   └──────────┘   └──────────┘
```

## Components

### Frontend Layer

**Technology**: React 18 with Vite

**Key Features**:
- User authentication interface
- Problem browsing dashboard
- Code editor with syntax highlighting
- Real-time test results display
- AI feedback visualization

**State Management**: React useState and useEffect hooks for local state management

**Styling**: TailwindCSS for responsive design

**Why React**: Component-based architecture enables modular development and easy maintenance. Vite provides fast hot module replacement for improved development experience.

### Backend API

**Technology**: FastAPI (Python 3.11)

**Database**: PostgreSQL 15 with SQLAlchemy 2.0 (async)

**Caching**: Redis for session management and API response caching

**Authentication**: JWT tokens with bcrypt password hashing

**Why FastAPI**: Native async/await support is critical for handling concurrent AI requests without blocking. Automatic OpenAPI documentation generation simplifies API testing and integration.

### Code Execution Service

**Implementation**: Subprocess-based execution

**Security Features**:
- Timeout limits (10 seconds default)
- No network access
- Temporary file isolation
- Resource limits

**Process**:
1. User code wrapped in test harness
2. Executed in isolated subprocess
3. Results captured and parsed
4. Cleanup of temporary files

**Why Subprocess**: Simpler than Docker-in-Docker, sufficient isolation for capstone project scope, faster execution without container overhead.

### Static Analysis Pipeline

#### AST Analyzer

**Technology**: Python `ast` module

**Features Detected**:
- Loop count and nesting depth
- Recursion usage
- Data structures (dict, set, list)
- Conditionals and early exits
- Guard clauses
- List comprehensions
- Function calls

**Implementation**: Custom AST visitor pattern that traverses code tree and extracts structural features.

#### Complexity Analyzer

**Estimation Rules**:
- No loops/recursion → O(1)
- Single loop + hashmap → O(n)
- Single loop + sorting → O(n log n)
- Nested 2 loops → O(n²)
- Nested 3 loops → O(n³)
- Unknown recursion → O(2^n)

**Comparison**: Compares estimated complexity with problem's optimal complexity to calculate match score (0.0 to 1.0).

### AI Integration Layer

**Provider**: Azure OpenAI

**Model**: GPT-5 (gpt-5-chat deployment)

**Prompt Structure**:
```
System: You are an expert technical interview coach...

User Context:
- Problem description
- User code
- Test results
- AST features
- Complexity analysis

Task: Provide constructive feedback focusing on:
1. Correctness issues
2. Algorithm efficiency
3. Code quality
4. Learning recommendations
```

**Response Processing**:
- Structured feedback text
- Improvement suggestions list
- Error categorization

**Why Azure OpenAI**: Provides enterprise-grade reliability, supports multiple model versions, and offers better rate limits than consumer OpenAI.

### Database Schema

```sql
users
├── id (PK)
├── email (unique)
├── username (unique)
├── hashed_password
├── is_active
└── created_at

problems
├── id (PK)
├── title
├── slug (unique)
├── description
├── difficulty (easy/medium/hard)
├── tags (JSON array)
├── test_cases (JSON)
└── optimal_patterns (JSON)

submissions
├── id (PK)
├── user_id (FK → users)
├── problem_id (FK → problems)
├── code (text)
├── language
├── status
├── test_results (JSON)
├── all_tests_passed
└── created_at

analysis_results
├── id (PK)
├── submission_id (FK → submissions, unique)
├── ast_features (JSON)
├── estimated_time_complexity
├── estimated_space_complexity
├── complexity_match
├── feedback_text
└── improvement_suggestions (JSON array)

weakness_profiles
├── id (PK)
├── user_id (FK → users, unique)
├── error_frequency (JSON)
├── total_submissions
└── top_weaknesses (JSON array)
```

**Relationships**:
- One user → many submissions
- One problem → many submissions
- One submission → one analysis result
- One user → one weakness profile

### Security

**Authentication**:
- JWT tokens with 30-minute expiration
- Bcrypt password hashing (cost factor 12)
- Token-based API authentication

**Data Protection**:
- SQL injection prevention via SQLAlchemy ORM
- Input validation with Pydantic
- CORS middleware for frontend access control

**Code Execution Safety**:
- Subprocess isolation
- Timeout enforcement
- No network access for executed code
- Temporary file cleanup

## Data Flow

### Complete Submission Pipeline

1. **User submits code** via React frontend
2. **Frontend validation** ensures code is not empty
3. **Backend receives** POST request to `/api/submissions/`
4. **Submission record created** with status "running"
5. **Execution service** runs code against test cases
6. **Test results captured** and submission updated
7. **AST analyzer** extracts code structure features
8. **Complexity analyzer** estimates time/space complexity
9. **AI service** generates feedback using GPT-5
10. **Analysis record created** with all results
11. **Response returned** to frontend with complete analysis
12. **Frontend displays** results on feedback page

### Request/Response Flow

```
POST /api/submissions/
{
  "problem_id": 1,
  "code": "def solution()...",
  "language": "python"
}

↓ [Backend Processing: 2-5 seconds]

{
  "id": 123,
  "test_results": [...],
  "all_tests_passed": true,
  "passed_tests": 5,
  "total_tests": 5
}

GET /api/analysis/123

↓

{
  "ast_features": {...},
  "estimated_time_complexity": "O(n)",
  "complexity_match": 1.0,
  "feedback_text": "Excellent solution...",
  "improvement_suggestions": [...]
}
```

## Deployment Architecture

**Frontend**: Local development with Vite dev server

**Backend**: Docker Compose orchestration
- FastAPI container
- PostgreSQL container
- Redis container
- Shared network

**Database**: PostgreSQL 15 with persistent volume

**CI/CD**: Manual deployment (automated pipeline ready to implement)

## Scalability Considerations

**Current Limitations**:
- Single-instance backend
- Synchronous AI requests
- No load balancing

**Ready for Scale**:
- Stateless backend (horizontal scaling ready)
- Database connection pooling
- Redis caching reduces redundant AI calls
- Async FastAPI supports concurrent requests

**Future Improvements**:
- Message queue for long-running AI requests
- Background workers for analysis pipeline
- CDN for static assets
- Database read replicas

## Performance Metrics

**Average Latency**:
- Code execution: 0.5-2 seconds
- AST analysis: <100ms
- Complexity estimation: <50ms
- AI feedback: 2-5 seconds
- Total: 3-7 seconds per submission

**Resource Usage**:
- Backend memory: ~200MB base
- Database: ~50MB with 100 problems
- Redis: ~10MB cache

**Cost Per Query**:
- Code execution: $0 (local)
- AI feedback: ~$0.002 (Azure OpenAI)
- Total: ~$0.002 per submission