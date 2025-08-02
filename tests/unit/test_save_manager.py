"""Tests for the SaveManager class."""

import json
import os
import shutil
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from src.utils.save_manager import SaveManager


class TestSaveManager:
    """Test suite for SaveManager."""

    @pytest.fixture
    def temp_save_dir(self):
        """Create a temporary directory for save files."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def save_manager(self, temp_save_dir):
        """Create SaveManager instance with temp directory."""
        return SaveManager(save_directory=temp_save_dir)

    def test_init_creates_directory(self, temp_save_dir):
        """Test that SaveManager creates save directory if it doesn't exist."""
        sub_dir = temp_save_dir / "subdir"
        assert not sub_dir.exists()

        SaveManager(save_directory=sub_dir)
        assert sub_dir.exists()

    def test_default_save_structure(self, save_manager):
        """Test that default save data has correct structure."""
        default_data = save_manager.default_save_data

        assert "version" in default_data
        assert "player" in default_data
        assert "settings" in default_data
        assert "progress" in default_data
        assert "high_scores" in default_data

        # Check nested structures
        assert "selected_character" in default_data["player"]
        assert "master_volume" in default_data["settings"]
        assert "minigames_unlocked" in default_data["progress"]
        # High scores are now initialized empty
        assert default_data["high_scores"] == {}

    def test_load_creates_new_save_when_none_exists(self, save_manager):
        """Test that load creates new save data when no file exists."""
        data = save_manager.load()

        assert data is not None
        assert data["version"] == SaveManager.SAVE_VERSION
        assert data["created_at"] is not None
        assert data["player"]["selected_character"] is None

    def test_save_and_load_roundtrip(self, save_manager):
        """Test saving and loading data works correctly."""
        # Load initial data
        save_manager.load()

        # Modify data
        save_manager.set_selected_character("danger")
        save_manager.set_setting("master_volume", 0.5)
        save_manager.unlock_minigame("ski")

        # Save
        assert save_manager.save() is True

        # Create new manager and load
        new_manager = SaveManager(save_directory=save_manager.save_directory)
        loaded_data = new_manager.load()

        assert loaded_data["player"]["selected_character"] == "danger"
        assert loaded_data["settings"]["master_volume"] == 0.5
        assert loaded_data["progress"]["minigames_unlocked"]["ski"] is True

    def test_high_score_management(self, save_manager):
        """Test high score addition and retrieval."""
        save_manager.load()

        # Add scores
        score1 = {"score": 1000, "date": "2025-07-28", "time": 45.2}
        score2 = {"score": 1500, "date": "2025-07-28", "time": 42.1}
        score3 = {"score": 800, "date": "2025-07-28", "time": 48.0}

        save_manager.add_high_score("ski", "danger", score1, "normal")
        save_manager.add_high_score("ski", "danger", score2, "normal")
        save_manager.add_high_score("ski", "danger", score3, "normal")

        # Check scores are sorted
        scores = save_manager.get_high_scores("ski", "danger", "normal")
        assert len(scores) == 3
        assert scores[0]["score"] == 1500
        assert scores[1]["score"] == 1000
        assert scores[2]["score"] == 800

    def test_high_score_limit(self, save_manager):
        """Test that only top 10 scores are kept."""
        save_manager.load()

        # Add 15 scores
        for i in range(15):
            score = {"score": i * 100, "date": "2025-07-28", "time": 50 - i}
            save_manager.add_high_score("pool", "rose", score, "easy")

        scores = save_manager.get_high_scores("pool", "rose", "easy")
        assert len(scores) == 10
        assert scores[0]["score"] == 1400  # Highest score
        assert scores[9]["score"] == 500  # 10th highest

    def test_corrupted_save_handling(self, save_manager, temp_save_dir):
        """Test handling of corrupted save files."""
        # Create corrupted save file
        save_file = temp_save_dir / SaveManager.SAVE_FILE_NAME
        with open(save_file, "w") as f:
            f.write("{ invalid json }")

        # Should handle gracefully and create new save
        data = save_manager.load()
        assert data is not None
        assert data["version"] == SaveManager.SAVE_VERSION

        # Check corrupted file was backed up
        corrupted_backup = temp_save_dir / f"{SaveManager.SAVE_FILE_NAME}.corrupted"
        assert corrupted_backup.exists()

    def test_save_backup_on_failure(self, save_manager):
        """Test that backup is restored if save fails."""
        save_manager.load()
        save_manager.set_selected_character("rose")
        save_manager.save()

        # Mock write failure
        with patch("builtins.open", side_effect=OSError("Write failed")):
            result = save_manager.save()

        assert result is False

        # Original save should still exist
        new_manager = SaveManager(save_directory=save_manager.save_directory)
        data = new_manager.load()
        assert data["player"]["selected_character"] == "rose"

    def test_version_migration(self, save_manager, temp_save_dir):
        """Test save data migration from older versions."""
        # Create old version save
        old_save_data = {
            "version": "0.9.0",
            "player": {"selected_character": "dad"},
            "settings": {"master_volume": 0.8},
            # Missing some new fields
        }

        save_file = temp_save_dir / SaveManager.SAVE_FILE_NAME
        with open(save_file, "w") as f:
            json.dump(old_save_data, f)

        # Load should migrate
        data = save_manager.load()

        # Check migration
        assert data["version"] == SaveManager.SAVE_VERSION
        assert data["player"]["selected_character"] == "dad"  # Preserved
        assert data["settings"]["master_volume"] == 0.8  # Preserved
        assert "high_scores" in data  # Added missing field
        assert "progress" in data  # Added missing field

    def test_deep_merge_preserves_values(self, save_manager):
        """Test that deep merge preserves existing values."""
        base = {"a": 1, "b": {"c": 2, "d": 3}, "e": [1, 2, 3]}
        update = {"a": 10, "b": {"c": 20, "f": 30}, "g": 40}

        result = save_manager._deep_merge_dicts(base, update)

        assert result["a"] == 10  # Updated
        assert result["b"]["c"] == 20  # Updated
        assert result["b"]["d"] == 3  # Preserved from base
        assert result["b"]["f"] == 30  # Added from update
        assert result["g"] == 40  # Added from update
        assert result["e"] == [1, 2, 3]  # Preserved from base

    def test_convenience_methods(self, save_manager):
        """Test all convenience methods work correctly."""
        save_manager.load()

        # Settings
        save_manager.set_setting("fullscreen", True)
        assert save_manager.get_setting("fullscreen") is True
        assert save_manager.get_setting("nonexistent", "default") == "default"

        # Character
        save_manager.set_selected_character("danger")
        assert save_manager.get_selected_character() == "danger"

        # Minigames
        assert save_manager.is_minigame_unlocked("vegas") is False
        save_manager.unlock_minigame("vegas")
        assert save_manager.is_minigame_unlocked("vegas") is True

    @pytest.mark.skipif(
        os.name != "nt", reason="Windows-specific test cannot run on Linux/Mac"
    )
    def test_default_save_directory_windows(self, temp_save_dir):
        """Test default save directory selection on Windows."""
        with patch("os.name", "nt"):
            with patch.dict("os.environ", {"APPDATA": str(temp_save_dir)}):
                manager = SaveManager()
                assert "DangerRose" in str(manager.save_directory)

    @pytest.mark.skipif(
        os.name == "nt", reason="Linux-specific test cannot run on Windows"
    )
    def test_default_save_directory_linux(self, temp_save_dir):
        """Test default save directory selection on Linux."""
        with patch("os.name", "posix"):
            with patch("platform.system", return_value="Linux"):
                with patch.dict("os.environ", {"XDG_CONFIG_HOME": str(temp_save_dir)}):
                    with patch("src.utils.save_manager.Path") as mock_path:
                        mock_path.return_value = temp_save_dir / "danger-rose"
                        manager = SaveManager(
                            save_directory=temp_save_dir / "danger-rose"
                        )
                        assert "danger-rose" in str(manager.save_directory)

    def test_datetime_serialization(self, save_manager):
        """Test that datetime values are properly serialized."""
        data = save_manager.load()

        # Check created_at is valid ISO format
        created_at = data["created_at"]
        parsed = datetime.fromisoformat(created_at)
        assert isinstance(parsed, datetime)

        # Save and check updated_at
        save_manager.save()

        # Reload and verify
        new_data = save_manager.load()
        updated_at = new_data["updated_at"]
        parsed_updated = datetime.fromisoformat(updated_at)
        assert isinstance(parsed_updated, datetime)
        assert parsed_updated >= parsed
