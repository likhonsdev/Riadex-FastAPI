# Riadex FastAPI Backend

A complete FastAPI + DDD backend scaffold with SSE chat, tool invocation, sandbox environments, and Gemini-through-OpenAI compatibility.

## Features

- **Session Management**: Create and manage conversation sessions with MongoDB persistence
- **Real-time Chat**: Server-Sent Events (SSE) streaming for real-time conversations
- **Tool Invocation**: Support for browser automation, shell commands, file operations, and web search
- **Sandbox Environment**: Docker containers for isolated code execution
- **VNC Visualization**: WebSocket-based remote viewing of sandbox environments
- **AI Integration**: Gemini AI through OpenAI-compatible API with streaming support
- **Domain-Driven Design**: Clean architecture with separated layers

## API Endpoints

### Session Management
- `PUT /api/v1/sessions` - Create new session
- `GET /api/v1/sessions/{session_id}` - Get session with history
- `GET /api/v1/sessions` - List all sessions
- `DELETE /api/v1/sessions/{session_id}` - Delete session
- `POST /api/v1/sessions/{session_id}/stop` - Stop active session

### Chat
- `POST /api/v1/sessions/{session_id}/chat` - Send message (SSE streaming)

### Tools
- `POST /api/v1/sessions/{session_id}/shell` - View shell session output
- `POST /api/v1/sessions/{session_id}/file` - View file content
- `WebSocket /api/v1/sessions/{session_id}/vnc` - VNC connection

## Quick Start

1. **Install dependencies**:
   \`\`\`bash
   pip install -r requirements.txt
   playwright install --with-deps chromium
   \`\`\`

2. **Set up environment**:
   \`\`\`bash
   cp .env.example .env
   # Edit .env with your configuration
   \`\`\`

3. **Start services**:
   \`\`\`bash
   # Using Docker Compose
   docker-compose up -d
   
   # Or run locally
   uvicorn api.main:app --reload
   \`\`\`

## Architecture

### Core Features
- **Session Management**: Create and manage conversation session instances
- **Real-time Conversation**: Implement real-time conversation through Server-Sent Events (SSE)
- **Tool Invocation**: Support for various tool calls, including:
  - Browser automation operations (using Playwright)
  - Shell command execution and viewing
  - File read/write operations
  - Web search integration
- **Sandbox Environment**: Use Docker containers to provide isolated execution environments
- **VNC Visualization**: Support remote viewing of the sandbox environment via WebSocket connection

### Requirements
- Python 3.9+
- Docker 20.10+
- MongoDB 4.4+
- Redis 6.0+

### Response Format

All APIs return responses in a unified format:

\`\`\`json
{
  "code": 0,
  "msg": "success",
  "data": {...}
}
\`\`\`

### SSE Events

The chat endpoint streams the following event types:
- `message`: Text message from assistant
- `title`: Session title update
- `plan`: Execution plan with steps
- `step`: Step status update
- `tool`: Tool invocation information
- `error`: Error information
- `done`: Conversation completion

## Development

### Adding New Tools

1. Define the tool interface in the `domain/external` directory
2. Implement the tool functionality in the infrastructure layer
3. Integrate the tool in `application/services`

### Project Structure

\`\`\`
api/
├── domain/                 # Domain layer
│   ├── entities/          # Domain entities
│   └── repositories/      # Repository interfaces
├── application/           # Application layer
│   └── services/         # Application services
├── infrastructure/       # Infrastructure layer
│   ├── database.py       # MongoDB connection
│   ├── redis_client.py   # Redis client
│   └── repositories/     # Repository implementations
└── presentation/         # Presentation layer
    ├── routers/          # API routes
    └── schemas/          # Request/response schemas
