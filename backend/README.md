# YT2Spot Backend API

FastAPI-based backend server providing REST API endpoints for the YouTube Music to Spotify migration tool.

## Overview

The backend handles OAuth authentication, file processing, migration logic, and real-time progress tracking for the YT2Spot application.

## Features

- **REST API**: Comprehensive API for migration operations
- **OAuth Integration**: Secure Spotify and YouTube Music authentication
- **File Processing**: Multi-format input parsing (CSV, JSON, TXT)
- **Real-time Updates**: Progress tracking with WebSocket-like polling
- **Session Management**: Stateful migration sessions with progress persistence
- **Error Handling**: Comprehensive error reporting and recovery

## Technology Stack

- **FastAPI**: Modern Python web framework with automatic API documentation
- **Pydantic**: Data validation and serialization with type hints
- **Python-multipart**: File upload handling
- **Requests**: HTTP client for external API integration
- **Uvicorn**: High-performance ASGI server

## Installation

### Prerequisites

- Python 3.9 or higher
- Virtual environment (recommended)

### Setup

1. Create and activate virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Install YT2Spot core package:

```bash
cd ..
pip install -e .
```

## Configuration

Create a `.env` file in the project root with required environment variables:

```bash
# Spotify API Configuration
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/api/auth/spotify/callback

# Application Settings
YT2SPOT_LOG_LEVEL=INFO
YT2SPOT_HARD_THRESHOLD=0.87
YT2SPOT_REJECT_THRESHOLD=0.60
```

## Usage

### Development Server

```bash
python main.py
```

The server will start on `http://localhost:8000` with:

- Automatic reload on code changes
- Interactive API documentation at `/docs`
- Alternative API docs at `/redoc`

### Production Deployment

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Core Migration

- `POST /upload` - Upload and parse music files
- `POST /migrate/start` - Start migration session
- `GET /migrate/status/{session_id}` - Get migration progress
- `POST /migrate/decision` - Submit user decisions
- `GET /migrate/results/{session_id}` - Get final results

### Authentication

- `GET /api/auth/spotify` - Initiate Spotify OAuth flow
- `GET /api/auth/spotify/callback` - Handle OAuth callback
- `GET /api/auth/youtube-music` - YouTube Music OAuth (placeholder)

### System

- `GET /` - Health check endpoint

## Data Models

### Migration Session

```python
class MigrationSession:
    session_id: str
    status: str  # "processing", "completed", "error", "awaiting_decision"
    songs: List[Song]
    progress: Dict[str, Any]
    results: List[Dict[str, Any]]
```

### Migration Status

```python
class MigrationStatus:
    session_id: str
    status: str
    progress: Dict[str, Any]
    current_song: Optional[Dict[str, Any]]
    pending_decision: Optional[Dict[str, Any]]
```

### Match Decision

```python
class MatchDecision:
    session_id: str
    action: str  # "accept", "reject", "skip"
    selected_track_id: Optional[str]
```

## Session Management

The backend maintains migration sessions in memory with the following lifecycle:

1. **Upload**: File parsing and song extraction
2. **Processing**: Track searching and matching
3. **Decision**: User interaction for ambiguous matches
4. **Completion**: Final results and cleanup

Sessions are automatically cleaned up after completion or timeout.

## OAuth Implementation

### Spotify OAuth Flow

1. Frontend requests authorization URL
2. User redirects to Spotify for authentication
3. Spotify returns authorization code to callback
4. Backend exchanges code for access token
5. User information and playlists are retrieved
6. Token and data returned to frontend

### Security Features

- State parameter validation
- Secure token handling
- CORS configuration for frontend integration
- Environment-based configuration

## Error Handling

The API provides comprehensive error responses with:

- HTTP status codes following REST conventions
- Detailed error messages for debugging
- Graceful handling of external API failures
- Session recovery for transient errors

### Common Error Responses

```json
{
  "detail": "Session not found",
  "status_code": 404
}
```

```json
{
  "detail": "Migration not completed",
  "status_code": 400
}
```

## File Processing

### Supported Formats

**CSV Files**:

- Headers: title, artist, album, duration
- Comma-separated values
- Optional quoted strings

**JSON Files**:

- Array of song objects
- Required fields: title, artist
- Optional fields: album, duration

**TXT Files**:

- Line-separated song entries
- Format: "Title - Artist" or "Title by Artist"
- Automatic parsing of common formats

### Upload Limits

- Maximum file size: 10MB
- Supported extensions: .csv, .json, .txt
- Character encoding: UTF-8

## Performance

### Optimization Features

- Async request handling for concurrent processing
- Connection pooling for external APIs
- Efficient memory management for large files
- Background task processing for long operations

### Monitoring

- Request logging with structured data
- Performance metrics tracking
- Error rate monitoring
- Session statistics

## Development

### Code Structure

```
backend/
├── main.py              # FastAPI application and routes
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Dependencies

Core dependencies in `requirements.txt`:

- `fastapi[all]` - Web framework with extras
- `uvicorn[standard]` - ASGI server
- `python-multipart` - File upload support
- `requests` - HTTP client for OAuth
- `pydantic` - Data validation

### Testing

```bash
# Run unit tests
pytest

# Run with coverage
pytest --cov=backend

# Run integration tests
pytest tests/integration/
```

### Debugging

Enable debug mode by setting environment variable:

```bash
export FASTAPI_ENV=development
```

This enables:

- Detailed error tracebacks
- Auto-reload on code changes
- Enhanced logging output

## CORS Configuration

The backend is configured to accept requests from:

- `http://localhost:3000` (development frontend)
- `http://localhost:3001` (alternative frontend port)
- `http://127.0.0.1:3000` (local IP variant)

For production, update CORS origins in `main.py`.

## Contributing

1. Follow PEP 8 style guidelines
2. Add type hints to all functions
3. Include docstrings for public methods
4. Write tests for new endpoints
5. Update API documentation as needed
