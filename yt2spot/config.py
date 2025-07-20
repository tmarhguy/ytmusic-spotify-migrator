"""Configuration management for YT2Spot."""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib

import tomli_w
from rich.console import Console

from yt2spot.models import SessionConfig

console = Console()


class ConfigManager:
    """Manages configuration from multiple sources with proper precedence."""

    DEFAULT_CONFIG = {
        "matching": {
            "hard_threshold": 0.87,
            "reject_threshold": 0.60,
            "fuzzy_threshold": 0.80,
            "max_candidates": 5,
        },
        "playlists": {
            "default_name": "YT Music Liked Songs",
            "force_recreate": False,
            "public": True,
        },
        "logging": {
            "json": False,
            "log_dir": "logs",
            "verbose": False,
            "quiet": False,
            "debug": False,
        },
        "auth": {
            "client_id": "",
            "client_secret": "",
            "redirect_uri": "http://localhost:8888/callback",
            "cache_file": ".cache-yt2spot",
        },
    }

    def __init__(self) -> None:
        self.config_paths = [
            Path.cwd() / ".yt2spot.toml",
            Path.home() / ".yt2spot.toml",
        ]

    def load_config_file(self, path: Path | None = None) -> dict[str, Any]:
        """Load configuration from TOML file."""
        if path is None:
            # Try default locations
            for config_path in self.config_paths:
                if config_path.exists():
                    path = config_path
                    break
            else:
                return {}

        if not path.exists():
            return {}

        try:
            with open(path, "rb") as f:
                config = tomllib.load(f)
            console.print(f"[dim]Loaded config from: {path}[/dim]")
            return config
        except Exception as e:
            console.print(
                f"[yellow]Warning: Failed to load config from {path}: {e}[/yellow]"
            )
            return {}

    def load_env_vars(self) -> dict[str, Any]:
        """Load configuration from environment variables."""
        env_config: dict[str, Any] = {}

        # Define mapping of env vars to config structure
        env_mappings = {
            "YT2SPOT_CLIENT_ID": ("auth", "client_id"),
            "YT2SPOT_CLIENT_SECRET": ("auth", "client_secret"),
            "YT2SPOT_REDIRECT_URI": ("auth", "redirect_uri"),
            "YT2SPOT_CACHE_FILE": ("auth", "cache_file"),
            "YT2SPOT_PLAYLIST_NAME": ("playlists", "default_name"),
            "YT2SPOT_LOG_DIR": ("logging", "log_dir"),
            "YT2SPOT_HARD_THRESHOLD": ("matching", "hard_threshold"),
            "YT2SPOT_REJECT_THRESHOLD": ("matching", "reject_threshold"),
            "YT2SPOT_FUZZY_THRESHOLD": ("matching", "fuzzy_threshold"),
            "YT2SPOT_MAX_CANDIDATES": ("matching", "max_candidates"),
        }

        for env_var, (section, key) in env_mappings.items():
            value = os.getenv(env_var)
            if value is not None:
                if section not in env_config:
                    env_config[section] = {}

                # Type conversion for numeric values
                if key.endswith("_threshold") or key == "max_candidates":
                    try:
                        env_config[section][key] = (
                            float(value) if "threshold" in key else int(value)
                        )
                    except ValueError:
                        console.print(
                            f"[yellow]Warning: Invalid value for {env_var}: {value}[/yellow]"
                        )
                        continue
                else:
                    env_config[section][key] = value

        return env_config

    def merge_configs(self, *configs: dict[str, Any]) -> dict[str, Any]:
        """Merge multiple configuration dictionaries with deep merging."""
        result = {}

        for config in configs:
            for section, values in config.items():
                if section not in result:
                    result[section] = {}

                if isinstance(values, dict):
                    result[section].update(values)
                else:
                    result[section] = values

        return result

    def create_session_config(
        self, input_path: str, cli_overrides: dict[str, Any] | None = None
    ) -> SessionConfig:
        """Create a SessionConfig by merging all sources."""
        # Load configurations in precedence order (lowest to highest)
        default_config = self.DEFAULT_CONFIG
        file_config = self.load_config_file()
        env_config = self.load_env_vars()
        cli_config = cli_overrides or {}

        # Merge all configurations
        merged = self.merge_configs(default_config, file_config, env_config, cli_config)

        # Create SessionConfig object
        return SessionConfig(
            input_path=input_path,
            playlist_name=merged["playlists"]["default_name"],
            log_dir=merged["logging"]["log_dir"],
            cache_file=merged["auth"]["cache_file"],
            hard_threshold=merged["matching"]["hard_threshold"],
            reject_threshold=merged["matching"]["reject_threshold"],
            fuzzy_threshold=merged["matching"]["fuzzy_threshold"],
            max_candidates=merged["matching"]["max_candidates"],
            public_playlist=merged["playlists"]["public"],
            force_recreate=merged["playlists"]["force_recreate"],
            verbose=merged["logging"]["verbose"],
            quiet=merged["logging"]["quiet"],
            debug=merged["logging"]["debug"],
            json_logs=merged["logging"]["json"],
            client_id=merged["auth"]["client_id"],
            client_secret=merged["auth"]["client_secret"],
            redirect_uri=merged["auth"]["redirect_uri"],
        )

    def create_sample_config(self, path: Path) -> None:
        """Create a sample configuration file."""
        sample_config = {
            "matching": {
                "hard_threshold": 0.87,
                "reject_threshold": 0.60,
                "fuzzy_threshold": 0.80,
                "max_candidates": 5,
            },
            "playlists": {
                "default_name": "YT Music Liked Songs",
                "force_recreate": False,
                "public": True,
            },
            "logging": {
                "json": False,
                "log_dir": "logs",
                "verbose": False,
                "quiet": False,
                "debug": False,
            },
            "auth": {
                "client_id": "your_spotify_client_id",
                "client_secret": "your_spotify_client_secret",
                "redirect_uri": "http://localhost:8888/callback",
                "cache_file": ".cache-yt2spot",
            },
        }

        with open(path, "wb") as f:
            tomli_w.dump(sample_config, f)

        console.print(f"[green]Created sample config at: {path}[/green]")
        console.print(
            "[yellow]Remember to update the auth section with your Spotify credentials![/yellow]"
        )


def load_config(
    input_path: str, cli_overrides: dict[str, Any] | None = None
) -> SessionConfig:
    """Convenience function to load configuration."""
    manager = ConfigManager()
    return manager.create_session_config(input_path, cli_overrides)
