# 🎵 YT2Spot

[![PyPI](https://img.shields.io/pypi/v/yt2spot.svg)](https://pypi.org/project/yt2spot/)
[![Python](https://img.shields.io/pypi/pyversions/yt2spot.svg)](https://pypi.org/project/yt2spot/)
[![License](https://img.shields.io/github/license/tyronemarhguy/yt2spot.svg)](LICENSE)
[![Tests](https://img.shields.io/github/workflow/status/tyronemarhguy/yt2spot/Tests)](https://github.com/tyronemarhguy/yt2spot/actions)

**Migrate your YouTube Music liked songs to Spotify playlists with intelligent fuzzy matching.**

YT2Spot is a command-line tool that reads a text export of your YouTube Music liked songs and creates a corresponding Spotify playlist using sophisticated matching algorithms to find the best track matches.

## ✨ Features

- 🎯 **Intelligent Matching**: Advanced fuzzy string matching with configurable thresholds
- 🔄 **Multiple Modes**: Automatic, interactive, and dry-run modes
- 📊 **Detailed Reporting**: Comprehensive logs of matched, unmatched, and ambiguous songs
- ⚡ **Smart Retry Logic**: Robust handling of API rate limits and network issues
- 🔧 **Highly Configurable**: CLI arguments, config files, and environment variables
- 📝 **Incremental Updates**: Re-run to add only new songs without duplicates
- 🎨 **Rich Terminal Output**: Beautiful progress bars and colored output
- 🔒 **Privacy First**: All processing happens locally, no cloud storage

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

## 📥 Getting Your YouTube Music Export

To export your liked songs from YouTube Music:

1. Go to [Google Takeout](https://takeout.google.com)
2. Select "YouTube and YouTube Music"
3. Choose "music-library-songs" → "liked songs"
4. Download and extract the archive
5. Find the text file with your liked songs

The expected format is:
```
Song Title - Artist Name
Another Song - Another Artist (Official Video)
```

## 🎛️ Configuration

YT2Spot supports multiple configuration methods (in order of precedence):

1. **CLI Arguments**: `--hard-threshold 0.9`
2. **Environment Variables**: `YT2SPOT_HARD_THRESHOLD=0.9`
3. **Config File**: `.yt2spot.toml`
4. **Built-in Defaults**

### Configuration Options

| Setting | Default | Description |
|---------|---------|-------------|
| `hard_threshold` | 0.87 | Auto-accept threshold (0.0-1.0) |
| `reject_threshold` | 0.60 | Auto-reject threshold (0.0-1.0) |
| `fuzzy_threshold` | 0.80 | Fuzzy matching minimum (0.0-1.0) |
| `max_candidates` | 5 | Max search results per song |
| `playlist_name` | "YT Music Liked Songs" | Target playlist name |
| `public` | true | Make playlist public |

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
git clone https://github.com/tyronemarhguy/yt2spot.git
cd yt2spot
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

| Version | Features |
|---------|----------|
| v0.1.0 | ✅ MVP: Basic migration, CLI, configuration |
| v0.2.0 | 🚧 Enhanced fuzzy matching, comprehensive logging |
| v0.3.0 | 📋 Interactive mode, incremental updates |
| v0.4.0 | ⚙️ Config file system, environment overrides |
| v0.5.0 | 🏃 Multi-threaded processing, performance improvements |
| v0.6.0 | 🔌 Plugin system for other music services |
| v1.0.0 | 🎯 Production ready, full test coverage |

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

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This tool is for personal use only. Ensure you have the rights to the music you're migrating. YT2Spot is not affiliated with YouTube, Google, or Spotify.

## 🙋‍♂️ Support

- 📖 [Documentation](https://github.com/tyronemarhguy/yt2spot/wiki)
- 🐛 [Issue Tracker](https://github.com/tyronemarhguy/yt2spot/issues)
- 💬 [Discussions](https://github.com/tyronemarhguy/yt2spot/discussions)

---

**Made with ❤️ for music lovers who want to keep their playlists in sync.**
