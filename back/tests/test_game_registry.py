"""Tests for game registry and configuration."""

import tempfile
from pathlib import Path

import pytest
import yaml

from src.games.registry import GameRegistry, GamesConfig, GameConfig


class TestGamesConfig:
    """Tests for GamesConfig validation."""

    def test_valid_config(self):
        """Test valid configuration."""
        config = GamesConfig.model_validate({
            "games": {
                "guess_number": {
                    "enabled": True,
                    "default": True,
                    "display_name": "Guess the Number",
                }
            }
        })
        
        assert config.games["guess_number"].enabled is True
        assert config.games["guess_number"].default is True

    def test_no_enabled_games(self):
        """Test config with no enabled games fails validation."""
        with pytest.raises(ValueError, match="At least one game must be enabled"):
            GamesConfig.model_validate({
                "games": {
                    "guess_number": {
                        "enabled": False,
                        "default": False,
                        "display_name": "Guess the Number",
                    }
                }
            })

    def test_no_default_game(self):
        """Test config with no default game fails validation."""
        with pytest.raises(ValueError, match="Exactly one game must be marked as default"):
            GamesConfig.model_validate({
                "games": {
                    "guess_number": {
                        "enabled": True,
                        "default": False,
                        "display_name": "Guess the Number",
                    }
                }
            })

    def test_multiple_default_games(self):
        """Test config with multiple default games fails validation."""
        with pytest.raises(ValueError, match="Only one game can be marked as default"):
            GamesConfig.model_validate({
                "games": {
                    "game1": {
                        "enabled": True,
                        "default": True,
                        "display_name": "Game 1",
                    },
                    "game2": {
                        "enabled": True,
                        "default": True,
                        "display_name": "Game 2",
                    }
                }
            })

    def test_disabled_default_game(self):
        """Test config where default game is disabled fails validation."""
        with pytest.raises(ValueError, match="must be enabled"):
            GamesConfig.model_validate({
                "games": {
                    "guess_number": {
                        "enabled": False,
                        "default": True,
                        "display_name": "Guess the Number",
                    }
                }
            })


class TestGameRegistry:
    """Tests for GameRegistry."""

    def test_load_config_success(self, tmp_path: Path):
        """Test loading a valid config file."""
        config_file = tmp_path / "games.yaml"
        config_file.write_text(yaml.dump({
            "games": {
                "guess_number": {
                    "enabled": True,
                    "default": True,
                    "display_name": "Guess the Number",
                    "settings": {
                        "min_target": 1,
                        "max_target": 100,
                    }
                }
            }
        }))
        
        registry = GameRegistry()
        registry.load_config(config_file)
        
        assert registry.default_game_type == "guess_number"
        assert "guess_number" in registry.enabled_games
        assert registry.get_settings("guess_number") == {"min_target": 1, "max_target": 100}

    def test_load_config_file_not_found(self):
        """Test loading a non-existent config file."""
        registry = GameRegistry()
        
        with pytest.raises(FileNotFoundError):
            registry.load_config(Path("/nonexistent/games.yaml"))

    def test_load_config_invalid(self, tmp_path: Path):
        """Test loading an invalid config file."""
        config_file = tmp_path / "games.yaml"
        config_file.write_text(yaml.dump({
            "games": {
                "guess_number": {
                    "enabled": True,
                    "default": False,  # No default!
                    "display_name": "Guess the Number",
                }
            }
        }))
        
        registry = GameRegistry()
        
        with pytest.raises(ValueError):
            registry.load_config(config_file)

    def test_register_game(self):
        """Test registering a game implementation."""
        from src.games.guess_number import GuessNumberGame
        
        registry = GameRegistry()
        game = GuessNumberGame()
        
        registry.register(game)
        
        assert registry.get_game("guess_number") is game

    def test_register_duplicate_game(self):
        """Test registering a game with the same type twice."""
        from src.games.guess_number import GuessNumberGame
        
        registry = GameRegistry()
        game1 = GuessNumberGame()
        game2 = GuessNumberGame()
        
        registry.register(game1)
        
        with pytest.raises(ValueError, match="already registered"):
            registry.register(game2)

    def test_validate_registration_success(self, tmp_path: Path):
        """Test successful registration validation."""
        from src.games.guess_number import GuessNumberGame
        
        config_file = tmp_path / "games.yaml"
        config_file.write_text(yaml.dump({
            "games": {
                "guess_number": {
                    "enabled": True,
                    "default": True,
                    "display_name": "Guess the Number",
                }
            }
        }))
        
        registry = GameRegistry()
        registry.load_config(config_file)
        registry.register(GuessNumberGame())
        
        # Should not raise
        registry.validate_registration()

    def test_validate_registration_missing_implementation(self, tmp_path: Path):
        """Test validation fails when enabled game has no implementation."""
        config_file = tmp_path / "games.yaml"
        config_file.write_text(yaml.dump({
            "games": {
                "nonexistent_game": {
                    "enabled": True,
                    "default": True,
                    "display_name": "Nonexistent Game",
                }
            }
        }))
        
        registry = GameRegistry()
        registry.load_config(config_file)
        
        with pytest.raises(ValueError, match="has no implementation"):
            registry.validate_registration()

    def test_is_game_enabled(self, tmp_path: Path):
        """Test checking if a game is enabled."""
        config_file = tmp_path / "games.yaml"
        config_file.write_text(yaml.dump({
            "games": {
                "enabled_game": {
                    "enabled": True,
                    "default": True,
                    "display_name": "Enabled Game",
                },
                "disabled_game": {
                    "enabled": False,
                    "default": False,
                    "display_name": "Disabled Game",
                }
            }
        }))
        
        registry = GameRegistry()
        registry.load_config(config_file)
        
        assert registry.is_game_enabled("enabled_game") is True
        assert registry.is_game_enabled("disabled_game") is False
        assert registry.is_game_enabled("nonexistent") is False


class TestGuessNumberGame:
    """Tests for GuessNumberGame implementation."""

    def test_game_properties(self):
        """Test basic game properties."""
        from src.games.guess_number import GuessNumberGame
        
        game = GuessNumberGame()
        
        assert game.game_type == "guess_number"
        assert game.display_name == "Guess the Number"
        assert len(game.get_available_actions()) == 2

    def test_can_start_game(self, session):
        """Test can_start_game check."""
        from src.games.guess_number import GuessNumberGame
        from src.models import Room, Player
        
        game = GuessNumberGame()
        room = Room()
        
        # No players
        can_start, error = game.can_start_game(room)
        assert can_start is False
        assert "at least 2 players" in error.lower()
        
        # One player
        room.players.append(Player(name="Player1"))
        can_start, error = game.can_start_game(room)
        assert can_start is False
        
        # Two players
        room.players.append(Player(name="Player2"))
        can_start, error = game.can_start_game(room)
        assert can_start is True
        assert error is None

