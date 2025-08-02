"""Integration tests for high score system."""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest

from src.utils.high_score_manager import HighScoreManager, ScoreEntry
from src.utils.save_manager import SaveManager


class TestHighScoreIntegration:
    """Test high score system integration with save manager."""

    @pytest.fixture
    def temp_save_dir(self):
        """Create a temporary directory for save files."""
        import shutil

        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        # Cleanup
        shutil.rmtree(temp_dir)

    @pytest.fixture
    def integrated_system(self, temp_save_dir):
        """Create integrated save and high score managers."""
        save_manager = SaveManager(save_directory=temp_save_dir)
        high_score_manager = HighScoreManager(save_manager)
        return save_manager, high_score_manager

    def test_high_score_persistence(self, integrated_system):
        """Test that high scores persist through save/load cycles."""
        save_manager, high_score_manager = integrated_system

        # Submit some scores
        scores = [
            ScoreEntry(
                "Player1", 45.5, "danger", "ski", "normal", datetime.now(), 45.5
            ),
            ScoreEntry(
                "Player2", 42.3, "danger", "ski", "normal", datetime.now(), 42.3
            ),
            ScoreEntry("Player3", 1500, "rose", "pool", "hard", datetime.now(), 120.0),
        ]

        for score in scores:
            high_score_manager.submit_score(score)

        # Create new managers with same directory
        new_save_manager = SaveManager(save_directory=save_manager.save_directory)
        new_high_score_manager = HighScoreManager(new_save_manager)

        # Check ski scores persisted
        ski_scores = new_high_score_manager.get_leaderboard("ski", "danger", "normal")
        assert len(ski_scores) == 2
        assert ski_scores[0].score == 42.3  # Lower time is better

        # Check pool scores persisted
        pool_scores = new_high_score_manager.get_leaderboard("pool", "rose", "hard")
        assert len(pool_scores) == 1
        assert pool_scores[0].score == 1500

    def test_save_migration_with_high_scores(self, temp_save_dir):
        """Test that old save format migrates correctly."""
        # Create old format save file
        import json

        old_save_data = {
            "version": "0.9.0",
            "player": {"selected_character": "danger"},
            "settings": {"master_volume": 0.8},
            "high_scores": {
                "ski": {
                    "danger": [
                        {"score": 45.5, "date": "2025-07-28"},
                        {"score": 50.0, "date": "2025-07-27"},
                    ],
                    "rose": [],
                    "dad": [],
                },
                "pool": {"danger": [], "rose": [], "dad": []},
                "vegas": {"danger": [], "rose": [], "dad": []},
            },
        }

        save_file = temp_save_dir / SaveManager.SAVE_FILE_NAME
        with open(save_file, "w") as f:
            json.dump(old_save_data, f)

        # Load with new system
        save_manager = SaveManager(save_directory=temp_save_dir)
        high_score_manager = HighScoreManager(save_manager)

        # Check migration worked
        scores = high_score_manager.get_leaderboard("ski", "danger", "normal")
        assert len(scores) == 2
        assert scores[0].score == 45.5
        assert scores[1].score == 50.0

        # Check new difficulty structure
        easy_scores = high_score_manager.get_leaderboard("ski", "danger", "easy")
        assert len(easy_scores) == 0
