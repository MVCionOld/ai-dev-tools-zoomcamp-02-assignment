# GitHub Copilot Custom Instructions

This file contains custom instructions for GitHub Copilot to provide better context-aware suggestions for this project.

## General Guidelines

- Follow best practices for code quality and maintainability
- Write clear, self-documenting code with meaningful variable and function names
- Include appropriate error handling and input validation
- Add comments for complex logic or non-obvious implementations
- Follow the DRY (Don't Repeat Yourself) principle

## Code Style

- Use consistent indentation (spaces or tabs as per project convention)
- Follow naming conventions appropriate for the programming language
- Keep functions and methods focused on a single responsibility
- Organize code in a logical and readable structure

## Documentation

- Document public APIs, functions, and classes
- Include usage examples where helpful
- Keep documentation up-to-date with code changes
- Write clear commit messages following conventional commit format

## Testing

- Write unit tests for new functionality
- Ensure tests are meaningful and cover edge cases
- Maintain or improve code coverage
- Follow existing test patterns and conventions

## Security

- Never commit sensitive information (API keys, passwords, secrets)
- Validate and sanitize user inputs
- Follow security best practices for the technology stack
- Be mindful of common vulnerabilities (XSS, SQL injection, etc.)

## Performance

- Consider performance implications of code changes
- Optimize where necessary but prioritize readability
- Avoid premature optimization
- Profile before optimizing

# Project Specification: Online Coding Interview Platform (CoderPad Clone)

## Project Overview
Build a full-stack online coding interview platform with real-time collaborative code editing, code execution, and session management. The application should have a Google-inspired clean UI and support multiple programming languages.

## Technology Stack

### Frontend
- **React 18+** with TypeScript
- **Monaco Editor** for code editing with syntax highlighting
- **react-markdown** with **remark-gfm** for markdown rendering
- **react-simplemde-editor** or **@uiw/react-md-editor** for markdown editing
- **ShareDB** for real-time collaborative editing (OT/CRDT)
- **WebSocket** client for real-time communication
- **Vite** as build tool
- **TailwindCSS** for styling (Google Material Design inspired)
- **React Query** for API state management
- **Axios** for HTTP requests with OpenAPI client generation

### Backend
- **FastAPI** (Python 3.13+) with async/await
- **uv** for Python project management
- **WebSocket** server (FastAPI WebSocket support)
- **SQLAlchemy 2.0** ORM with async support
- **Alembic** for database migrations
- **PostgreSQL 15+** for persistent storage
- **Redis 7+** for session management, pub/sub, and ShareDB backend
- **Pydantic v2** for data validation
- **Docker SDK for Python** for code execution in isolated containers

### Infrastructure & DevOps
- **Docker** and **Docker Compose** for local development
- **Docker-in-Docker** or Docker socket mounting for code execution
- **OpenAPI 3.1** specification with auto-generation
- **pytest** with pytest-asyncio for backend testing
- **pytest-cov** for code coverage
- **Jest** and **React Testing Library** for frontend testing
- **Playwright** for E2E tests
- **pre-commit** hooks for code quality

## Architecture

### System Design
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Monaco Editor│  │  ShareDB     │  │  WebSocket   │      │
│  │              │  │  Client      │  │  Client      │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ┌──────────────┐  ┌──────────────┐                        │
│  │ MD Editor    │  │  MD Renderer │                        │
│  │ (Creator)    │  │  (Viewers)   │                        │
│  └──────────────┘  └──────────────┘                        │
└─────────────────────────────────────────────────────────────┘
                              │
                    ┌─────────┴─────────┐
                    │   OpenAPI / REST  │
                    │   WebSocket       │
                    └─────────┬─────────┘
┌─────────────────────────────┴─────────────────────────────┐
│                    Backend (FastAPI)                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ REST API     │  │  WebSocket   │  │  ShareDB     │    │
│  │ Endpoints    │  │  Handler     │  │  Server      │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐    │
│  │ Session Mgmt │  │ Code Executor│  │  Auth        │    │
│  └──────────────┘  └──────────────┘  └──────────────┘    │
│  ┌──────────────────────────────────────────────────┐    │
│  │       Execution Engine (Plugin Architecture)      │    │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  │    │
│  │  │  Python    │  │ JavaScript │  │  SQL       │  │    │
│  │  │  Executor  │  │  Executor  │  │  Executor  │  │    │
│  │  │  (Active)  │  │  (Future)  │  │  (Future)  │  │    │
│  │  └────────────┘  └────────────┘  └────────────┘  │    │
│  └──────────────────────────────────────────────────┘    │
└────────────────────────────────────────────────────────────┘
              │                 │                 │
    ┌─────────┴────────┐  ┌────┴─────┐  ┌────────┴────────┐
    │   PostgreSQL     │  │  Redis   │  │ Docker Engine   │
    │   (Persistent)   │  │ (Cache)  │  │ (Execution)     │
    └──────────────────┘  └──────────┘  └─────────────────┘
```

## Project Structure

```
rivendell/
├── frontend/                      # React application
│   ├── src/
│   │   ├── components/
│   │   │   ├── Editor/
│   │   │   │   ├── MonacoEditor.tsx
│   │   │   │   ├── CollaborativeEditor.tsx
│   │   │   │   └── LanguageSelector.tsx
│   │   │   ├── Problem/
│   │   │   │   ├── ProblemEditor.tsx      # MD editor for creator
│   │   │   │   ├── ProblemViewer.tsx      # MD renderer for viewers
│   │   │   │   └── ProblemPanel.tsx       # Container component
│   │   │   ├── Session/
│   │   │   │   ├── SessionCreate.tsx
│   │   │   │   ├── SessionJoin.tsx
│   │   │   │   └── SessionInfo.tsx
│   │   │   ├── Output/
│   │   │   │   ├── ExecutionOutput.tsx
│   │   │   │   └── ErrorDisplay.tsx
│   │   │   └── Layout/
│   │   │       ├── Header.tsx
│   │   │       ├── Sidebar.tsx
│   │   │       ├── SplitPane.tsx          # Resizable panels
│   │   │       └── MainLayout.tsx
│   │   ├── hooks/
│   │   │   ├── useWebSocket.ts
│   │   │   ├── useShareDB.ts
│   │   │   ├── useCodeExecution.ts
│   │   │   └── useProblemSync.ts
│   │   ├── services/
│   │   │   ├── api.ts              # OpenAPI generated client
│   │   │   ├── websocket.ts
│   │   │   └── sharedb.ts
│   │   ├── types/
│   │   │   └── api.d.ts            # Generated from OpenAPI
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── e2e/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── backend/                       # FastAPI application (Python 3.13+)
│   ├── app/
│   │   ├── api/
│   │   │   ├── v1/
│   │   │   │   ├── endpoints/
│   │   │   │   │   ├── sessions.py
│   │   │   │   │   ├── execute.py
│   │   │   │   │   ├── problems.py        # Problem text CRUD
│   │   │   │   │   └── health.py
│   │   │   │   └── api.py
│   │   │   └── deps.py
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── events.py
│   │   ├── db/
│   │   │   ├── base.py
│   │   │   ├── session.py
│   │   │   └── init_db.py
│   │   ├── models/
│   │   │   ├── session.py
│   │   │   ├── user.py
│   │   │   ├── problem.py                 # Problem statement model
│   │   │   └── code_snapshot.py
│   │   ├── schemas/
│   │   │   ├── session.py
│   │   │   ├── execution.py
│   │   │   ├── problem.py
│   │   │   └── websocket.py
│   │   ├── services/
│   │   │   ├── session_service.py
│   │   │   ├── executor/
│   │   │   │   ├── base.py                # Abstract executor interface
│   │   │   │   ├── python_executor.py     # Python 3.13 implementation
│   │   │   │   ├── registry.py            # Executor plugin registry
│   │   │   │   └── __init__.py
│   │   │   ├── sharedb_service.py
│   │   │   ├── problem_service.py
│   │   │   └── redis_service.py
│   │   ├── websocket/
│   │   │   ├── connection_manager.py
│   │   │   ├── handlers.py
│   │   │   └── sharedb_integration.py
│   │   └── main.py
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_executor/
│   │   │   │   ├── test_base.py
│   │   │   │   ├── test_python_executor.py
│   │   │   │   └── test_registry.py
│   │   │   └── test_services/
│   │   ├── integration/
│   │   └── conftest.py
│   ├── alembic/
│   │   └── versions/
│   ├── pyproject.toml             # uv project file (Python 3.13+)
│   ├── uv.lock
│   └── pytest.ini
│
├── executor/                      # Code execution Docker images
│   ├── base/
│   │   └── Dockerfile.base        # Common base image
│   ├── python/
│   │   ├── Dockerfile.python313   # Python 3.13 executor
│   │   └── requirements.txt
│   ├── javascript/                # Future support
│   │   └── Dockerfile.node
│   ├── sql/                       # Future SQL execution support
│   │   ├── Dockerfile.postgres
│   │   ├── Dockerfile.mysql
│   │   └── Dockerfile.sqlite
│   └── templates/
│       └── runner.py              # Standard execution wrapper
│
├── docker-compose.yml
├── docker-compose.dev.yml
├── .env.example
└── README.md
```

## Core Features & Requirements

### 1. Session Management
- **Create Session**: Generate unique shareable link (UUID-based)
- **Join Session**: Allow multiple users to join via link
- **Session Roles**: Creator (host) vs Participant (viewer)
- **Session State**: Store in PostgreSQL (metadata) and Redis (active state)
- **Session Expiry**: Auto-cleanup after 24 hours of inactivity

**Database Schema**:
```python
class Session(Base):
    id: UUID (PK)
    name: str
    created_at: datetime
    expires_at: datetime
    language: str  # "python3.13", "javascript", "sql-postgres", etc.
    code_snapshot: Text (periodic saves)
    problem_text: Text (markdown content)
    creator_id: UUID (FK to User)
    is_active: bool

class User(Base):
    id: UUID (PK)
    session_id: UUID (FK)
    role: Enum["creator", "participant"]
    joined_at: datetime
    last_seen: datetime
```

### 2. Problem Statement Management
- **Markdown Support**: Full GitHub-flavored markdown
- **Creator Privileges**: Only session creator can edit problem text
- **Real-time Sync**: Problem updates broadcast to all participants
- **Persistence**: Store in PostgreSQL, sync via Redis pub/sub

**Features**:
- Code blocks with syntax highlighting
- Tables, lists, checkboxes
- LaTeX math support (optional, using KaTeX)
- Image embedding (via URL)
- Collapsible sections

**API Endpoints**:
```python
PUT  /api/v1/sessions/{id}/problem  - Update problem text (creator only)
GET  /api/v1/sessions/{id}/problem  - Get current problem text
```

**WebSocket Events**:
```python
{
    "type": "problem_updated",
    "data": {
        "session_id": "uuid",
        "problem_text": "markdown string",
        "updated_by": "user_id",
        "timestamp": "iso8601"
    }
}
```

### 3. Real-Time Collaborative Editing
- **ShareDB Integration**:
  - Use Redis as ShareDB backend
  - Implement Operational Transformation for conflict resolution
  - Support multiple cursors/selections
  - Separate ShareDB documents for code and problem text
- **WebSocket Events**:
  - `cursor_move`: Broadcast cursor positions
  - `selection_change`: Share text selections
  - `user_join`: Notify when user joins
  - `user_leave`: Notify when user leaves
  - `code_change`: Synchronize via ShareDB
  - `problem_updated`: Broadcast problem text changes

### 4. Code Execution (Plugin Architecture)

**Design Principles**:
- **Extensible**: Easy to add new languages/executors
- **Isolated**: Each executor is a separate plugin
- **Secure**: Sandboxed execution in Docker containers
- **Configurable**: Resource limits per executor type

**Base Executor Interface** (`app/services/executor/base.py`):
```python
from abc import ABC, abstractmethod
from typing import Protocol
from pydantic import BaseModel

class ExecutionRequest(BaseModel):
    code: str
    stdin: str | None = None
    timeout: int = 10
    memory_limit: str = "256m"

class ExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    memory_used_kb: int
    error: str | None = None

class BaseExecutor(ABC):
    """Abstract base class for all code executors"""

    language: str  # e.g., "python3.13", "sql-postgres"
    docker_image: str
    default_timeout: int = 10
    default_memory: str = "256m"

    @abstractmethod
    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute code in isolated environment"""
        pass

    @abstractmethod
    async def validate_code(self, code: str) -> tuple[bool, str | None]:
        """Pre-execution validation (syntax check, forbidden imports)"""
        pass

    @abstractmethod
    def get_resource_limits(self) -> dict:
        """Return Docker resource limits"""
        pass
```

**Python 3.13 Executor** (`app/services/executor/python_executor.py`):
```python
import docker
import asyncio
from .base import BaseExecutor, ExecutionRequest, ExecutionResult

class Python313Executor(BaseExecutor):
    language = "python3.13"
    docker_image = "rivendell/python:3.13-executor"

    # Security: whitelist of allowed packages
    ALLOWED_PACKAGES = [
        "math", "itertools", "collections", "functools",
        "heapq", "bisect", "re", "json", "datetime"
    ]

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        """Execute Python code in Docker container"""
        client = docker.from_env()

        try:
            # Create container with resource limits
            container = client.containers.run(
                image=self.docker_image,
                command=["python", "-c", request.code],
                stdin_open=True,
                stdout=True,
                stderr=True,
                detach=True,
                network_disabled=True,
                mem_limit=request.memory_limit,
                cpu_quota=50000,  # 0.5 CPU
                read_only=True,
                tmpfs={'/tmp': 'size=10M'},
                remove=True,
            )

            # Wait with timeout
            result = await asyncio.wait_for(
                asyncio.to_thread(container.wait),
                timeout=request.timeout
            )

            stdout = container.logs(stdout=True, stderr=False).decode()
            stderr = container.logs(stdout=False, stderr=True).decode()

            return ExecutionResult(
                stdout=stdout,
                stderr=stderr,
                exit_code=result['StatusCode'],
                execution_time_ms=self._calculate_time(),
                memory_used_kb=self._get_memory_stats(container)
            )

        except asyncio.TimeoutError:
            container.kill()
            return ExecutionResult(
                stdout="",
                stderr="",
                exit_code=-1,
                execution_time_ms=request.timeout * 1000,
                memory_used_kb=0,
                error="Execution timed out"
            )

    async def validate_code(self, code: str) -> tuple[bool, str | None]:
        """Check for syntax errors and forbidden imports"""
        # AST-based validation
        import ast
        try:
            tree = ast.parse(code)
            # Check for forbidden imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        if not self._is_allowed_import(alias.name):
                            return False, f"Import '{alias.name}' not allowed"
            return True, None
        except SyntaxError as e:
            return False, f"Syntax error: {str(e)}"
```

**Executor Registry** (`app/services/executor/registry.py`):
```python
from typing import Dict, Type
from .base import BaseExecutor
from .python_executor import Python313Executor

class ExecutorRegistry:
    """Plugin registry for code executors"""

    _executors: Dict[str, Type[BaseExecutor]] = {}

    @classmethod
    def register(cls, executor_class: Type[BaseExecutor]):
        """Register a new executor"""
        cls._executors[executor_class.language] = executor_class

    @classmethod
    def get_executor(cls, language: str) -> BaseExecutor:
        """Get executor instance for language"""
        if language not in cls._executors:
            raise ValueError(f"Unsupported language: {language}")
        return cls._executors[language]()

    @classmethod
    def list_supported_languages(cls) -> list[str]:
        """List all registered languages"""
        return list(cls._executors.keys())

# Auto-register Python executor
ExecutorRegistry.register(Python313Executor)

# Future executors will be registered here:
# ExecutorRegistry.register(JavaScriptExecutor)
# ExecutorRegistry.register(PostgreSQLExecutor)
# ExecutorRegistry.register(MySQLExecutor)
```

**Future Executor Examples** (Placeholders for easy expansion):

```python
# JavaScript/Node.js Executor (Future)
class JavaScriptExecutor(BaseExecutor):
    language = "javascript"
    docker_image = "rivendell/node:22-executor"
    # Implementation similar to Python executor

# SQL Executors (Future)
class PostgreSQLExecutor(BaseExecutor):
    language = "sql-postgres"
    docker_image = "rivendell/postgres:15-executor"

    async def execute(self, request: ExecutionRequest) -> ExecutionResult:
        # Create temp database, run query, return results
        pass

class MySQLExecutor(BaseExecutor):
    language = "sql-mysql"
    docker_image = "rivendell/mysql:8-executor"

class SQLiteExecutor(BaseExecutor):
    language = "sql-sqlite"
    docker_image = "rivendell/sqlite:3-executor"
```

**Docker Images**:
```dockerfile
# executor/python/Dockerfile.python313
FROM python:3.13-slim

# Install only allowed packages
RUN pip install --no-cache-dir numpy pandas

# Create non-root user
RUN useradd -m -u 1000 executor
USER executor

WORKDIR /workspace

# Entrypoint for execution
COPY runner.py /usr/local/bin/
ENTRYPOINT ["python", "/usr/local/bin/runner.py"]
```

**Execution Schema**:
```python
class ExecutionRequest(BaseModel):
    session_id: UUID
    code: str
    language: str  # "python3.13", "javascript", "sql-postgres"
    stdin: str | None = None

class ExecutionResult(BaseModel):
    stdout: str
    stderr: str
    exit_code: int
    execution_time_ms: int
    memory_used_kb: int
    error: str | None = None
```

### 5. Frontend UI Components

**Google Material Design Inspired**:
- Clean white background with subtle shadows
- Blue accent color (#1a73e8)
- Roboto font family
- Card-based layouts
- Smooth transitions
- Resizable split panes

**Main Layout - Editor View** (3-panel split):
```
┌────────────────────────────────────────────────────────────┐
│  Header: [Session Name] [Language: Python 3.13 ▼] [Run]   │
│          [Share Link: copy] [Users: 👤 👤]                 │
├────────────────────────┬───────────────────────────────────┤
│                        │                                   │
│  Problem Statement     │   Monaco Code Editor              │
│  (Markdown Rendered)   │                                   │
│                        │   1 | def solution(nums):         │
│  # Two Sum             │   2 |     # Your code here        │
│                        │   3 |     pass                    │
│  Given an array...     │   4 |                             │
│                        │                                   │
│  **Example:**          │                                   │
│  ```                   │                                   │
│  Input: [2,7,11,15]    │                                   │
│  Output: [0,1]         │                                   │
│  ```                   │                                   │
│                        │                                   │
│  [Edit] (creator only) │                                   │
│                        │                                   │
├────────────────────────┴───────────────────────────────────┤
│  Output / Console                                          │
│  ────────────────────────────────────────────────────────  │
│  > Running...                                              │
│  > [0, 1]                                                  │
│  > Execution time: 23ms                                    │
└────────────────────────────────────────────────────────────┘
```

**Panel Proportions**:
- Left (Problem): 25-30% width
- Center (Editor): 45-50% width
- Right/Bottom (Output): 20-25% height (bottom panel) or right panel

**Components**:

1. **ProblemPanel.tsx**:
```typescript
interface ProblemPanelProps {
  sessionId: string;
  isCreator: boolean;
  problemText: string;
  onProblemUpdate: (text: string) => void;
}

// Renders markdown or shows editor based on mode
```

2. **ProblemViewer.tsx**:
```typescript
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';

// Renders markdown with syntax highlighting
```

3. **ProblemEditor.tsx**:
```typescript
import MDEditor from '@uiw/react-md-editor';

// Live preview markdown editor for creators
// Toggle between edit/preview modes
```

4. **SplitPane.tsx**:
```typescript
import { ResizablePanel, ResizablePanelGroup } from 'react-resizable-panels';

// Configurable split layout with drag handles
```

### 6. OpenAPI Specification
- Auto-generate OpenAPI 3.1 spec from FastAPI
- Use `openapi-typescript` to generate TypeScript types
- Include all REST endpoints and schemas
- Document WebSocket protocols separately

**API Endpoints**:
```
POST   /api/v1/sessions              - Create session
GET    /api/v1/sessions/{id}         - Get session
PUT    /api/v1/sessions/{id}/problem - Update problem (creator only)
GET    /api/v1/sessions/{id}/problem - Get problem text
POST   /api/v1/sessions/{id}/execute - Execute code
GET    /api/v1/sessions/{id}/snapshots - Get code history
GET    /api/v1/executors             - List supported languages
WS     /ws/sessions/{id}             - WebSocket connection
GET    /api/v1/health                - Health check
GET    /openapi.json                 - OpenAPI spec
```

### 7. Testing Requirements

**Backend Tests (Python 3.13)**:
```python
# Unit Tests (pytest)
## Executor Tests
- test_python313_executor_basic()
- test_python313_executor_timeout()
- test_python313_executor_memory_limit()
- test_python313_forbidden_imports()
- test_executor_registry()
- test_executor_plugin_loading()

## Session Tests
- test_session_creation()
- test_session_expiry()
- test_session_roles()
- test_problem_text_update_authorization()

## Service Tests
- test_sharedb_operations()
- test_redis_pubsub()

# Integration Tests
- test_websocket_connection()
- test_collaborative_editing()
- test_end_to_end_execution()
- test_problem_sync_across_clients()
- test_database_transactions()

# Coverage Target: 85%+
```

**Frontend Tests**:
```typescript
// Unit Tests (Jest)
- MonacoEditor.test.tsx
- ProblemViewer.test.tsx
- ProblemEditor.test.tsx
- useWebSocket.test.ts
- SessionService.test.ts

// Integration Tests (React Testing Library)
- SessionFlow.test.tsx
- CollaborativeEditing.test.tsx
- ProblemEditingFlow.test.tsx

// E2E Tests (Playwright)
- session-creation.spec.ts
- code-execution-python.spec.ts
- multi-user-collaboration.spec.ts
- problem-statement-editing.spec.ts
- creator-permissions.spec.ts

// Coverage Target: 80%+
```

### 8. Local Development Setup

**Using Host Machine**:
```bash
# Backend (Python 3.13+)
cd backend
uv sync --python 3.13
uv run alembic upgrade head
uv run uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev

# Services (separate terminals)
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15
docker run -d -p 6379:6379 redis:7

# Build executor images
cd executor/python
docker build -t rivendell/python:3.13-executor -f Dockerfile.python313 .
```

**Using Docker Compose**:
```bash
docker-compose -f docker-compose.dev.yml up
# Hot reload enabled for both frontend and backend
# PostgreSQL, Redis auto-configured
# Executor images pre-built
```

**docker-compose.dev.yml**:
```yaml
services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: rivendell
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    volumes:
      - ./backend:/app
      - /var/run/docker.sock:/var/run/docker.sock  # For code execution
    ports:
      - "8000:8000"
    environment:
      - PYTHON_VERSION=3.13
      - DATABASE_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/rivendell
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - postgres
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.dev
    volumes:
      - ./frontend:/app
      - /app/node_modules
    ports:
      - "5173:5173"
    environment:
      - VITE_API_URL=http://localhost:8000
    command: npm run dev -- --host

  executor-builder:
    build:
      context: ./executor/python
      dockerfile: Dockerfile.python313
    image: rivendell/python:3.13-executor

volumes:
  postgres_data:
```

### 9. Environment Configuration

**.env.example**:
```bash
# Python Version
PYTHON_VERSION=3.13

# Database
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/rivendell
DATABASE_POOL_SIZE=20

# Redis
REDIS_URL=redis://localhost:6379/0
REDIS_PUBSUB_CHANNEL=sharedb

# Application
SECRET_KEY=your-secret-key-change-in-production
SESSION_EXPIRE_HOURS=24
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Code Execution
DOCKER_HOST=unix:///var/run/docker.sock
EXECUTION_TIMEOUT=10
EXECUTION_MEMORY_LIMIT=256m
PYTHON_EXECUTOR_IMAGE=rivendell/python:3.13-executor

# Supported Languages (comma-separated)
SUPPORTED_LANGUAGES=python3.13

# Future expansion (commented out)
# SUPPORTED_LANGUAGES=python3.13,javascript,sql-duckdb,sql-sqlite

# Monitoring
LOG_LEVEL=INFO
SENTRY_DSN=

# Feature Flags
ENABLE_PROBLEM_EDITING=true
ENABLE_CODE_SNAPSHOTS=true
```

## Implementation Priorities

### Phase 1: Core Infrastructure
1. Set up uv project with Python 3.13 and FastAPI
2. Configure PostgreSQL with SQLAlchemy 2.0 (async)
3. Set up Redis connection and pub/sub
4. Create basic React app with Vite + TypeScript
5. Implement OpenAPI spec generation
6. Set up pytest and coverage tools

### Phase 2: Session & Problem Management
1. Implement session CRUD operations with roles
2. Create problem text model and API endpoints
3. Build session UI components with role-based rendering
4. Implement ProblemViewer and ProblemEditor components
5. Add WebSocket connection manager
6. Write comprehensive tests for session and problem logic

### Phase 3: Collaborative Editing
1. Integrate ShareDB with Redis backend
2. Connect Monaco Editor to ShareDB for code
3. Implement problem text real-time sync
4. Add cursor/selection broadcasting
5. Build user presence indicators
6. Test multi-user scenarios with 5+ concurrent users

### Phase 4: Code Execution Engine
1. Design and implement BaseExecutor interface
2. Create ExecutorRegistry with plugin system
3. Build Python313Executor with Docker integration
4. Create Python 3.13 executor Docker image
5. Implement resource limits and timeout handling
6. Add execution API endpoint with validation
7. Write security-focused tests (forbidden imports, resource exhaustion)
8. Test Docker isolation and cleanup

### Phase 5: UI Polish & Integration
1. Implement resizable split pane layout
2. Add markdown rendering with syntax highlighting
3. Build output panel with execution history
4. Implement creator-only problem editing controls
5. Add loading states and error boundaries
6. Optimize WebSocket reconnection logic

### Phase 6: Testing & Documentation
1. Achieve 85%+ backend code coverage
2. Achieve 80%+ frontend code coverage
3. Set up E2E test suite with Playwright
4. Write integration tests for full user flows
5. Create API documentation from OpenAPI spec
6. Write deployment and scaling guides
7. Performance testing and optimization

## Code Quality Requirements

- **Type Safety**:
  - Full TypeScript strict mode for frontend
  - Type hints with mypy strict mode for Python backend
  - Pydantic v2 for all API schemas

- **Linting & Formatting**:
  - Frontend: ESLint + Prettier with Airbnb config
  - Backend: Ruff (replaces Black, isort, flake8)

- **Pre-commit Hooks**:
  - Format, lint, type check before commit
  - Run quick tests on changed files

- **Documentation**:
  - Docstrings (Google style) for all public functions
  - README with architecture diagrams
  - API documentation from OpenAPI

- **Error Handling**:
  - Proper exception hierarchy
  - Structured logging with context
  - Graceful degradation

- **Security**:
  - Input validation with Pydantic
  - SQL injection prevention (SQLAlchemy ORM)
  - XSS protection (React auto-escaping)
  - Docker security best practices
  - Rate limiting on execution endpoints

## Extensibility Guidelines

### Adding New Language Executors

**Step 1**: Create executor class
```python
# app/services/executor/javascript_executor.py
from .base import BaseExecutor

class JavaScriptExecutor(BaseExecutor):
    language = "javascript"
    docker_image = "rivendell/node:22-executor"
    # Implement abstract methods
```

**Step 2**: Create Docker image
```dockerfile
# executor/javascript/Dockerfile.node
FROM node:22-slim
# Setup isolated environment
```

**Step 3**: Register in registry
```python
# app/services/executor/registry.py
from .javascript_executor import JavaScriptExecutor
ExecutorRegistry.register(JavaScriptExecutor)
```

**Step 4**: Update configuration
```bash
# .env
SUPPORTED_LANGUAGES=python3.13,javascript
```

**Step 5**: Write tests
```python
# tests/unit/test_executor/test_javascript_executor.py
```

### Adding SQL Database Support

Similar process, but executor manages temporary database:
```python
class PostgreSQLExecutor(BaseExecutor):
    async def execute(self, request: ExecutionRequest):
        # 1. Spin up temp Postgres container
        # 2. Apply schema (if provided in stdin)
        # 3. Execute query
        # 4. Return results as formatted table
        # 5. Cleanup container
```

## Deliverables

1. ✅ Fully functional web application with 3-panel UI
2. ✅ Python 3.13 code execution with Docker isolation
3. ✅ Extensible executor plugin system
4. ✅ Problem statement editing with markdown support
5. ✅ Real-time collaboration for code and problem text
6. ✅ Complete test suites with 85%+ backend, 80%+ frontend coverage
7. ✅ Docker Compose setup for local development
8. ✅ OpenAPI specification and generated TypeScript clients
9. ✅ Comprehensive README with architecture and setup guides
10. ✅ Environment configuration templates
11. ✅ CI/CD pipeline configuration (GitHub Actions)

---

## START IMPLEMENTATION

**Phase 1 - Task 1**: Initialize backend uv project with Python 3.13

```bash
cd backend
uv init --python 3.13
uv add fastapi uvicorn sqlalchemy alembic asyncpg redis pydantic-settings docker pytest pytest-asyncio pytest-cov
```

Create the following initial structure:
1. `app/main.py` - FastAPI application entry point
2. `app/core/config.py` - Settings with pydantic-settings
3. `app/db/base.py` - SQLAlchemy Base and async engine setup
4. `app/models/session.py` - Session and User models
5. `app/services/executor/base.py` - BaseExecutor abstract class
6. `app/services/executor/registry.py` - ExecutorRegistry
7. `tests/conftest.py` - Pytest fixtures for database and Docker

**Acceptance Criteria**:
- ✅ Python 3.13 virtual environment created with uv
- ✅ All dependencies installed and locked
- ✅ FastAPI runs with health check endpoint
- ✅ PostgreSQL connection established (async)
- ✅ Redis connection established
- ✅ Basic pytest setup with coverage reporting
- ✅ Pre-commit hooks configured

Begin implementation now.
