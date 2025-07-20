# 🎵 YT2Spot

[![PyPI](https://img.shields.io/pypi/v/yt2spot.svg)](https://pypi.org/project/yt2spot/)
[![Python](https://img.shields.io/pypi/pyversions/yt2spot.svg)](https://pypi.org/project/yt2spot/)
[![License](https://img.shields.io/github/license/tmarhguy/ytmusic-spotify-migrator.svg)](LICENSE)
[![Tests](https://img.shields.io/github/workflow/status/tmarhguy/ytmusic-spotify-migrator/Tests)](https://github.com/tmarhguy/ytmusic-spotify-migrator/actions)

**Migrate your YouTube Music liked songs to Spotify playlists with intelligent fuzzy matching.**

YT2Spot is a command-line tool that reads a text export of your YouTube Music liked songs and creates a corresponding Spotify playlist using sophisticated matching algorithms to find the best track matches.

## 🎯 Features

### Core Migration Features

- **Multi-format input support**: CSV, JSON, TXT files
- **Intelligent track matching**: Advanced fuzzy matching algorithms
- **Playlist management**: Create, update, and organize Spotify playlists
- **Duplicate detection**: Prevents duplicate tracks in target playlists
- **Progress tracking**: Real-time migration progress with detailed logging
- **Error handling**: Graceful handling of API limits and network issues

### �️ Utility Tools

- **[Text-to-CSV Preprocessor](./tools/text-to-csv/)**: Clean and convert raw YouTube Music playlist exports into structured CSV format

## 🚀 Quick Start

### Installation

```bash
pip install yt2spot
```

### Setup

1. **Get Spotify API credentials** from [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. **Create configuration file**:
   ```bash
   yt2spot init-config
   ```
3. **Edit `.yt2spot.toml`** and add your Spotify credentials:
   ```toml
   [auth]
   client_id = "your_spotify_client_id"
   client_secret = "your_spotify_client_secret"
   ```

### Basic Usage

```bash
# Migrate your liked songs
yt2spot migrate --input liked_songs.txt

# Dry run to see what would happen
yt2spot migrate --input liked_songs.txt --dry-run --verbose

# Interactive mode for manual approval
yt2spot migrate --input liked_songs.txt --interactive

# Enable fuzzy matching for better results
yt2spot migrate --input liked_songs.txt --fuzzy --fuzzy-threshold 0.75
```

## 📥 Getting Your YouTube Music Data

### Option 1: Using Google Takeout (Recommended)

To export your liked songs from YouTube Music:

1. Go to [Google Takeout](https://takeout.google.com)
2. Select "YouTube and YouTube Music"
3. Choose "music-library-songs" → "liked songs"
4. Download and extract the archive
5. Find the text file with your liked songs

### Option 2: Manual Export with Preprocessing

If you have raw YouTube Music playlist data in text format, use our preprocessing tool:

1. Place your raw data in `tools/text-to-csv/music-taste.txt`
2. Run the text-to-csv preprocessor:
   ```bash
   cd tools/text-to-csv
   python cleaner.py
   ```
3. Use the generated `output.csv` with the main migration tool

The expected format after preprocessing is:

```csv
Title,Artist,Album,Duration
"Song Title","Artist Name","Album Name","3:45"
"Another Song","Another Artist","Single","4:12"
```

## 🎛️ Configuration

YT2Spot supports multiple configuration methods (in order of precedence):

1. **CLI Arguments**: `--hard-threshold 0.9`
2. **Environment Variables**: `YT2SPOT_HARD_THRESHOLD=0.9`
3. **Config File**: `.yt2spot.toml`
4. **Built-in Defaults**

### Configuration Options

| Setting            | Default                | Description                      |
| ------------------ | ---------------------- | -------------------------------- |
| `hard_threshold`   | 0.87                   | Auto-accept threshold (0.0-1.0)  |
| `reject_threshold` | 0.60                   | Auto-reject threshold (0.0-1.0)  |
| `fuzzy_threshold`  | 0.80                   | Fuzzy matching minimum (0.0-1.0) |
| `max_candidates`   | 5                      | Max search results per song      |
| `playlist_name`    | "YT Music Liked Songs" | Target playlist name             |
| `public`           | true                   | Make playlist public             |

### Sample Configuration

```toml
[matching]
hard_threshold = 0.87
reject_threshold = 0.60
fuzzy_threshold = 0.80
max_candidates = 5

[playlists]
default_name = "YT Music Liked Songs"
force_recreate = false
public = true

[logging]
json = false
log_dir = "logs"
verbose = false

[auth]
client_id = "your_spotify_client_id"
client_secret = "your_spotify_client_secret"
redirect_uri = "http://localhost:8888/callback"
```

## 🎯 Matching Algorithm

YT2Spot uses a sophisticated matching algorithm that considers:

1. **Title Similarity**: Normalized Levenshtein distance and token matching
2. **Artist Matching**: Primary and featured artist comparison
3. **Popularity Boost**: Slight preference for popular tracks (when similarity is high)
4. **Version Detection**: Penalties for live/remix/remaster mismatches
5. **Feature Extraction**: Smart parsing of "feat.", "ft.", and "featuring"

### Text Normalization

- Removes YouTube qualifiers: "(Official Video)", "[Official Audio]", etc.
- Extracts featured artists: "Song (feat. Artist)" → "Song" + ["Artist"]
- Handles "The" prefix: "The Beatles" → "Beatles, The"
- Casefold and punctuation normalization

### Decision Thresholds

- **≥ Hard Threshold**: Automatic acceptance
- **< Reject Threshold**: Automatic rejection → logged as unmatched
- **Between Thresholds**:
  - Interactive mode: User prompt
  - Fuzzy mode: Accept if above fuzzy threshold
  - Default: Log as unmatched

## 📊 Output & Reporting

YT2Spot generates comprehensive reports:

### Console Output

```
🎵 YT2Spot v0.1.0
YouTube Music → Spotify Migration Tool

Configuration:
  Input: liked_songs.txt
  Playlist: YT Music Liked Songs (public)
  Matching: hard=0.87, reject=0.60
  Mode: 🤖 Automatic + 🌊 Fuzzy

Processing... ████████████████████████████████ 742/742

=== YT2Spot Summary ===
Total input lines: 742
Valid songs parsed: 735
Matched (auto): 648
Fuzzy accepted: 34
Unmatched: 31
Accuracy: 704/735 = 95.8%
```

### Log Files

- `logs/session_summary.json` - Complete session statistics
- `logs/unmatched.txt` - Songs that couldn't be matched
- `logs/ambiguous.csv` - Detailed candidate information
- `logs/matched.csv` - All successful matches (optional)

## 🔧 CLI Reference

### Commands

- `yt2spot migrate` - Main migration command
- `yt2spot init-config` - Create sample configuration file

### Migration Options

```bash
# Required
-i, --input PATH          Input text file

# Playlist Options
-p, --playlist TEXT       Playlist name
--public / --private      Playlist visibility
--force-recreate          Recreate playlist from scratch

# Matching Options
--hard-threshold FLOAT    Auto-accept threshold (0.0-1.0)
--reject-threshold FLOAT  Auto-reject threshold (0.0-1.0)
--fuzzy-threshold FLOAT   Fuzzy minimum threshold (0.0-1.0)
--fuzzy                   Enable fuzzy matching
--interactive             Manual approval for ambiguous matches

# Control Options
--dry-run                 Simulate without changes
--limit INTEGER           Process only N songs
--config PATH             Custom config file path

# Output Options
-v, --verbose             Detailed output
-q, --quiet               Minimal output
--debug                   Debug information
--json-logs               Structured JSON logs
--log-dir PATH            Custom log directory
```

## 🛠️ Development

### Setup Development Environment

```bash
git clone https://github.com/tmarhguy/ytmusic-spotify-migrator.git
cd ytmusic-spotify-migrator
make setup
```

### Running Tests

```bash
make test          # Run tests with coverage
make test-fast     # Run tests without coverage
make quality       # Run linting and type checking
```

### Code Quality

```bash
make lint          # Check code style
make format        # Format code with black
make type-check    # Run mypy type checking
```

## 🗺️ Roadmap

| Version | Features                                               |
| ------- | ------------------------------------------------------ |
| v0.1.0  | ✅ MVP: Basic migration, CLI, configuration            |
| v0.2.0  | 🚧 Enhanced fuzzy matching, comprehensive logging      |
| v0.3.0  | 📋 Interactive mode, incremental updates               |
| v0.4.0  | ⚙️ Config file system, environment overrides           |
| v0.5.0  | 🏃 Multi-threaded processing, performance improvements |
| v0.6.0  | 🔌 Plugin system for other music services              |
| v1.0.0  | 🎯 Production ready, full test coverage                |

## 🤝 Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Workflow

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Make your changes
4. Run tests: `make test`
5. Run quality checks: `make quality`
6. Commit: `git commit -m "Add amazing feature"`
7. Push: `git push origin feature/amazing-feature`
8. Create a Pull Request

## � Project Structure

```
ytmusic-spotify-migrator/
├── yt2spot/                  # Main package
│   ├── cli.py               # Command-line interface
│   ├── config.py            # Configuration management
│   ├── models.py            # Data models
│   └── matcher/             # Matching algorithms
├── tools/                   # Utility tools
│   └── text-to-csv/         # Text preprocessing tool
├── tests/                   # Test suite
├── literature.md            # Project specification
├── pyproject.toml           # Project configuration
└── README.md               # This file
```

## �📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal use only. Ensure you have the rights to the music you're migrating. YT2Spot is not affiliated with YouTube, Google, or Spotify.

## 🙋‍♂️ Support

- 📖 [Documentation](https://github.com/tmarhguy/ytmusic-spotify-migrator/wiki)
- 🐛 [Issue Tracker](https://github.com/tmarhguy/ytmusic-spotify-migrator/issues)
- 💬 [Discussions](https://github.com/tmarhguy/ytmusic-spotify-migrator/discussions)

---

**Made with ❤️ for music lovers who want to keep their playlists in sync.**
