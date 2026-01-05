"""Game registry for managing available games."""

import logging
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, model_validator

from src.games.base import BaseGame

logger = logging.getLogger(__name__)


class GameConfig(BaseModel):
    """Configuration for a single game."""

    enabled: bool = True
    default: bool = False
    display_name: str
    description: str = ""
    settings: dict[str, Any] = Field(default_factory=dict)


class GamesConfig(BaseModel):
    """Root configuration for all games."""

    games: dict[str, GameConfig]

    @model_validator(mode="after")
    def validate_config(self) -> "GamesConfig":
        """Validate the games configuration."""
        enabled_games = [name for name, cfg in self.games.items() if cfg.enabled]
        default_games = [name for name, cfg in self.games.items() if cfg.default]

        if not enabled_games:
            raise ValueError("At least one game must be enabled")

        if len(default_games) == 0:
            raise ValueError("Exactly one game must be marked as default")

        if len(default_games) > 1:
            raise ValueError(
                f"Only one game can be marked as default, found: {default_games}"
            )

        default_game = default_games[0]
        if default_game not in enabled_games:
            raise ValueError(
                f"Default game '{default_game}' must be enabled"
            )

        return self


class GameRegistry:
    """
    Registry for game implementations.
    
    Loads configuration from games.yaml and registers game classes.
    Provides lookup for game instances and configuration.
    """

    def __init__(self):
        self._games: dict[str, BaseGame] = {}
        self._config: GamesConfig | None = None
        self._config_path: Path | None = None
        self._initialized: bool = False

    @property
    def is_initialized(self) -> bool:
        """Check if the registry has been initialized."""
        return self._initialized

    def load_config(self, config_path: Path | None = None) -> None:
        """
        Load games configuration from YAML file.
        
        Args:
            config_path: Path to games.yaml. If None, uses default location.
            
        Raises:
            FileNotFoundError: If config file doesn't exist
            ValueError: If config is invalid
        """
        if config_path is None:
            # Default: look for games.yaml in the back/ directory
            config_path = Path(__file__).parent.parent.parent / "games.yaml"

        self._config_path = config_path

        if not config_path.exists():
            raise FileNotFoundError(f"Games config file not found: {config_path}")

        with open(config_path) as f:
            raw_config = yaml.safe_load(f)

        self._config = GamesConfig.model_validate(raw_config)
        logger.info(
            f"Loaded games config: {len(self.enabled_games)} enabled, "
            f"default: {self.default_game_type}"
        )

    def register(self, game: BaseGame) -> None:
        """
        Register a game implementation.
        
        Args:
            game: Game instance to register
            
        Raises:
            ValueError: If game type is already registered
        """
        if game.game_type in self._games:
            raise ValueError(f"Game '{game.game_type}' is already registered")

        self._games[game.game_type] = game
        logger.info(f"Registered game: {game.game_type} ({game.display_name})")

    def get_game(self, game_type: str) -> BaseGame | None:
        """Get a game instance by type."""
        return self._games.get(game_type)

    def get_config(self, game_type: str) -> GameConfig | None:
        """Get configuration for a game type."""
        if self._config is None:
            return None
        return self._config.games.get(game_type)

    def get_settings(self, game_type: str) -> dict[str, Any]:
        """Get game-specific settings."""
        config = self.get_config(game_type)
        if config is None:
            return {}
        return config.settings

    @property
    def enabled_games(self) -> list[str]:
        """List of enabled game types."""
        if self._config is None:
            return []
        return [name for name, cfg in self._config.games.items() if cfg.enabled]

    @property
    def default_game_type(self) -> str | None:
        """The default game type."""
        if self._config is None:
            return None
        for name, cfg in self._config.games.items():
            if cfg.default:
                return name
        return None

    @property
    def default_game(self) -> BaseGame | None:
        """The default game instance."""
        default_type = self.default_game_type
        if default_type is None:
            return None
        return self.get_game(default_type)

    def is_game_enabled(self, game_type: str) -> bool:
        """Check if a game type is enabled."""
        config = self.get_config(game_type)
        return config is not None and config.enabled

    def validate_registration(self) -> None:
        """
        Validate that all enabled games have registered implementations.
        
        Raises:
            ValueError: If an enabled game has no implementation
        """
        for game_type in self.enabled_games:
            if game_type not in self._games:
                raise ValueError(
                    f"Game '{game_type}' is enabled in config but has no implementation"
                )
        self._initialized = True

    def get_all_games_info(self) -> list[dict[str, Any]]:
        """Get info about all enabled games for API responses."""
        result = []
        for game_type in self.enabled_games:
            game = self.get_game(game_type)
            config = self.get_config(game_type)
            if game and config:
                result.append({
                    "game_type": game_type,
                    "display_name": config.display_name,
                    "description": config.description,
                    "is_default": config.default,
                    "actions": game.get_available_actions(),
                })
        return result


# Global registry instance
game_registry = GameRegistry()


def register_all_games() -> None:
    """Register all game implementations."""
    from src.games.guess_number import GuessNumberGame

    game_registry.register(GuessNumberGame())
    # Add more games here as they are implemented

