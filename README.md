# YT2Spot - YouTube Music to Spotify Migration Tool

A comprehensive migration tool for transferring music libraries from YouTube Music to Spotify with intelligent matching algorithms and real-time web interface.

## Features

### Core Migration Capabilities
- **Multi-platform support**: Direct OAuth authentication with Spotify and file-based imports
- **Intelligent matching**: Advanced fuzzy matching algorithms with configurable thresholds
- **Real-time migration**: Live progress tracking with visual feedback
- **Interactive decisions**: Manual resolution for ambiguous matches
- **High success rates**: Optimized matching algorithms for accurate track identification

### Web Interface
- **Service selection**: Choose between direct platform authentication or file uploads
- **OAuth integration**: Secure authentication with Spotify API
- **Live dashboard**: Real-time visualization of migration progress
- **Progress tracking**: Song-by-song progress with success/failure indicators
- **Responsive design**: Modern web interface with intuitive user experience

### Command Line Interface
- **Batch processing**: Handle large music libraries efficiently
- **Flexible input**: Support for CSV, JSON, and TXT file formats
- **Detailed logging**: Comprehensive migration reports and error tracking
- **Configuration management**: Customizable matching parameters

## Architecture

### Frontend
- **Framework**: React 18 with TypeScript
- **Build System**: Vite for fast development and optimized builds
- **Styling**: Tailwind CSS with responsive design
- **State Management**: React hooks for application state

### Backend
- **API Framework**: FastAPI with async support
- **Authentication**: OAuth 2.0 implementation for secure platform access
- **Real-time Updates**: WebSocket-like polling for live progress
- **Database**: In-memory session management with persistent storage options

### Core Engine
- **Matching Engine**: Fuzzy string matching with multiple algorithms
- **Music Processing**: Metadata extraction and normalization
- **API Integration**: Spotify Web API client with rate limiting
- **Error Handling**: Comprehensive error recovery and reporting

## Installation

### Prerequisites
- Python 3.9 or higher
- Node.js 16 or higher
- Spotify Developer Account

### Backend Setup

1. Clone the repository:
```bash
git clone https://github.com/tmarhguy/ytmusic-spotify-migrator.git
cd ytmusic-spotify-migrator
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install Python dependencies:
```bash
pip install -e .
```

4. Install backend API dependencies:
```bash
cd backend
pip install -r requirements.txt
```

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

### Configuration

1. Copy the environment template:
```bash
cp .env.example .env
```

2. Configure Spotify API credentials in `.env`:
   - Create an app at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Add your Client ID and Client Secret to the `.env` file
   - Set the redirect URI to `http://localhost:8000/api/auth/spotify/callback`

## Usage

### Web Interface

1. Start the backend server:
```bash
cd backend
source venv/bin/activate
python main.py
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

3. Open your browser to `http://localhost:3000`

4. Follow the web interface to:
   - Select your source platform (Spotify, YouTube Music, or file upload)
   - Select your destination platform
   - Authenticate with OAuth (if using direct platform integration)
   - Monitor real-time migration progress

### Command Line Interface

1. Prepare your music data:
   - Export your YouTube Music library
   - Use the included text-to-CSV tool if needed: `tools/text-to-csv/`

2. Run the migration:
```bash
yt2spot migrate --input your_music_file.csv --playlist "Migrated Playlist"
```

3. Monitor progress and resolve any ambiguous matches interactively.

## File Formats

### Supported Input Formats

**CSV Format** (recommended):
```csv
title,artist,album,duration
"Bohemian Rhapsody","Queen","A Night at the Opera","355"
```

**JSON Format**:
```json
[
  {
    "title": "Bohemian Rhapsody",
    "artist": "Queen",
    "album": "A Night at the Opera",
    "duration": 355
  }
]
```

**TXT Format**:
```
Bohemian Rhapsody - Queen
```

## Configuration

### Matching Thresholds

Configure matching sensitivity in `.env`:

```bash
# Automatic acceptance threshold (0.0-1.0)
YT2SPOT_HARD_THRESHOLD=0.87

# Automatic rejection threshold (0.0-1.0)
YT2SPOT_REJECT_THRESHOLD=0.60

# Fuzzy matching threshold (0.0-1.0)
YT2SPOT_FUZZY_THRESHOLD=0.80
```

### API Configuration

```bash
# Spotify API settings
SPOTIFY_CLIENT_ID=your_client_id
SPOTIFY_CLIENT_SECRET=your_client_secret
SPOTIFY_REDIRECT_URI=http://localhost:8000/api/auth/spotify/callback

# Application settings
YT2SPOT_LOG_LEVEL=INFO
```

## API Documentation

The backend provides a comprehensive REST API. When running, visit:
- API Documentation: `http://localhost:8000/docs`
- Interactive API Explorer: `http://localhost:8000/redoc`

### Key Endpoints

- `POST /upload` - Upload music files for processing
- `POST /migrate/start` - Begin migration process
- `GET /migrate/status/{session_id}` - Check migration progress
- `GET /api/auth/spotify` - Initiate Spotify OAuth flow
- `POST /migrate/decision` - Submit user decisions for ambiguous matches

## Development

### Project Structure

```
ytmusic-spotify-migrator/
├── yt2spot/                 # Core Python package
│   ├── cli.py              # Command line interface
│   ├── config.py           # Configuration management
│   ├── spotify_client.py   # Spotify API integration
│   ├── input_parser.py     # File format parsers
│   └── matcher/            # Matching algorithms
├── backend/                 # FastAPI web server
│   ├── main.py             # API endpoints
│   └── requirements.txt    # Python dependencies
├── frontend/                # React web interface
│   ├── src/                # Source code
│   ├── package.json        # Node.js dependencies
│   └── vite.config.ts      # Build configuration
├── tools/                   # Utility tools
└── tests/                   # Test suites
```

### Running Tests

```bash
# Python tests
pytest

# Frontend tests
cd frontend
npm test
```

### Building for Production

```bash
# Build frontend
cd frontend
npm run build

# Package Python application
python -m build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Spotify Web API for music service integration
- FastAPI for high-performance API framework
- React and Vite for modern frontend development
- RapidFuzz for efficient string matching algorithms

## Support

For issues and questions:
- Create an issue on [GitHub Issues](https://github.com/tmarhguy/ytmusic-spotify-migrator/issues)
- Check the [documentation](https://github.com/tmarhguy/ytmusic-spotify-migrator/wiki)
