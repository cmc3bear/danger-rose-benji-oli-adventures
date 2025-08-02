"""Tests for the HighScoreManager class."""

from datetime import datetime
from unittest.mock import Mock

import pytest

from src.utils.high_score_manager import HighScoreManager, ScoreEntry


class TestHighScoreManager:
    """Test suite for HighScoreManager."""

    @pytest.fixture
    def mock_save_manager(self):
        """Create a mock SaveManager."""
        mock = Mock()
        mock._current_save_data = {"high_scores": {}}
        mock.save = Mock(return_value=True)
        mock.load = Mock()
        return mock

    @pytest.fixture
    def high_score_manager(self, mock_save_manager):
        """Create HighScoreManager instance with mock SaveManager."""
        return HighScoreManager(mock_save_manager)

    def test_score_entry_creation(self):
        """Test ScoreEntry dataclass creation."""
        entry = ScoreEntry(
            player_name="Player1",
            score=1000,
            character="danger",
            game_mode="ski",
            difficulty="normal",
            date=datetime.now(),
            time_elapsed=45.5,
        )

        assert entry.player_name == "Player1"
        assert entry.score == 1000
        assert entry.character == "danger"
        assert entry.game_mode == "ski"
        assert entry.difficulty == "normal"
        assert entry.time_elapsed == 45.5

    def test_submit_score(self, high_score_manager):
        """Test submitting a new score."""
        entry = ScoreEntry(
            player_name="TestPlayer",
            score=1500,
            character="danger",
            game_mode="ski",
            difficulty="normal",
            date=datetime.now(),
            time_elapsed=42.3,
        )

        is_high_score = high_score_manager.submit_score(entry)

        assert is_high_score is True
        assert high_score_manager.save_manager.save.called

    def test_submit_multiple_scores_sorting(self, high_score_manager):
        """Test that scores are properly sorted by game type."""
        # Submit time-based scores (ski - lower is better)
        ski_scores = [
            ScoreEntry(
                "Player1", 45.5, "danger", "ski", "normal", datetime.now(), 45.5
            ),
            ScoreEntry(
                "Player2", 40.2, "danger", "ski", "normal", datetime.now(), 40.2
            ),
            ScoreEntry(
                "Player3", 50.0, "danger", "ski", "normal", datetime.now(), 50.0
            ),
        ]

        for score in ski_scores:
            high_score_manager.submit_score(score)

        leaderboard = high_score_manager.get_leaderboard("ski", "danger", "normal")
        assert leaderboard[0].score == 40.2  # Fastest time first
        assert leaderboard[1].score == 45.5
        assert leaderboard[2].score == 50.0

        # Submit points-based scores (pool - higher is better)
        pool_scores = [
            ScoreEntry("Player1", 1000, "rose", "pool", "normal", datetime.now(), 60.0),
            ScoreEntry("Player2", 1500, "rose", "pool", "normal", datetime.now(), 55.0),
            ScoreEntry("Player3", 800, "rose", "pool", "normal", datetime.now(), 65.0),
        ]

        for score in pool_scores:
            high_score_manager.submit_score(score)

        leaderboard = high_score_manager.get_leaderboard("pool", "rose", "normal")
        assert leaderboard[0].score == 1500  # Highest score first
        assert leaderboard[1].score == 1000
        assert leaderboard[2].score == 800

    def test_get_leaderboard_filtering(self, high_score_manager):
        """Test leaderboard filtering by difficulty."""
        # Add scores with different difficulties
        scores = [
            ScoreEntry("Easy1", 1000, "danger", "pool", "easy", datetime.now(), 60.0),
            ScoreEntry(
                "Normal1", 1500, "danger", "pool", "normal", datetime.now(), 55.0
            ),
            ScoreEntry("Hard1", 2000, "danger", "pool", "hard", datetime.now(), 50.0),
            ScoreEntry("Easy2", 1200, "danger", "pool", "easy", datetime.now(), 58.0),
        ]

        for score in scores:
            high_score_manager.submit_score(score)

        # Get easy difficulty leaderboard
        easy_board = high_score_manager.get_leaderboard("pool", "danger", "easy")
        assert len(easy_board) == 2
        assert all(entry.difficulty == "easy" for entry in easy_board)

        # Get all difficulties
        all_board = high_score_manager.get_leaderboard("pool", "danger")
        assert len(all_board) == 4

    def test_is_high_score(self, high_score_manager):
        """Test checking if a score qualifies as a high score."""
        # Fill leaderboard with 10 scores
        for i in range(10):
            entry = ScoreEntry(
                f"Player{i}",
                1000 + i * 100,
                "danger",
                "pool",
                "normal",
                datetime.now(),
                60.0,
            )
            high_score_manager.submit_score(entry)

        # Score that beats the lowest
        assert (
            high_score_manager.is_high_score(1050, "pool", "danger", "normal") is True
        )

        # Score that doesn't beat the lowest
        assert (
            high_score_manager.is_high_score(900, "pool", "danger", "normal") is False
        )

        # Time-based game (ski) - lower is better
        for i in range(10):
            entry = ScoreEntry(
                f"SkiPlayer{i}",
                40.0 + i,
                "rose",
                "ski",
                "normal",
                datetime.now(),
                40.0 + i,
            )
            high_score_manager.submit_score(entry)

        # Better time (lower)
        assert high_score_manager.is_high_score(39.5, "ski", "rose", "normal") is True

        # Worse time (higher)
        assert high_score_manager.is_high_score(50.0, "ski", "rose", "normal") is False

    def test_get_rank(self, high_score_manager):
        """Test getting rank for a specific score."""
        # Add some scores
        scores = [1500, 1200, 1000, 800, 600]
        for i, score in enumerate(scores):
            entry = ScoreEntry(
                f"Player{i}", score, "dad", "pool", "normal", datetime.now(), 60.0
            )
            high_score_manager.submit_score(entry)

        # Test ranks
        assert high_score_manager.get_rank(1600, "pool", "dad", "normal") == 1
        assert high_score_manager.get_rank(1300, "pool", "dad", "normal") == 2
        assert high_score_manager.get_rank(900, "pool", "dad", "normal") == 4
        assert high_score_manager.get_rank(500, "pool", "dad", "normal") == 6

    def test_clear_scores(self, high_score_manager):
        """Test clearing scores for specific categories."""
        # Add scores
        entry1 = ScoreEntry(
            "Player1", 1000, "danger", "pool", "normal", datetime.now(), 60.0
        )
        entry2 = ScoreEntry(
            "Player2", 1500, "danger", "pool", "easy", datetime.now(), 55.0
        )
        entry3 = ScoreEntry(
            "Player3", 2000, "rose", "pool", "normal", datetime.now(), 50.0
        )

        high_score_manager.submit_score(entry1)
        high_score_manager.submit_score(entry2)
        high_score_manager.submit_score(entry3)

        # Clear specific category
        high_score_manager.clear_scores("pool", "danger", "normal")

        # Check cleared
        danger_normal = high_score_manager.get_leaderboard("pool", "danger", "normal")
        assert len(danger_normal) == 0

        # Check others remain
        danger_easy = high_score_manager.get_leaderboard("pool", "danger", "easy")
        assert len(danger_easy) == 1

        rose_normal = high_score_manager.get_leaderboard("pool", "rose", "normal")
        assert len(rose_normal) == 1

    def test_get_personal_best(self, high_score_manager):
        """Test getting personal best score for a player."""
        # Add multiple scores for same player
        scores = [
            ScoreEntry(
                "Player1", 1000, "danger", "pool", "normal", datetime.now(), 60.0
            ),
            ScoreEntry(
                "Player1", 1500, "danger", "pool", "normal", datetime.now(), 55.0
            ),
            ScoreEntry(
                "Player1", 800, "danger", "pool", "normal", datetime.now(), 65.0
            ),
            ScoreEntry(
                "Player2", 2000, "danger", "pool", "normal", datetime.now(), 50.0
            ),
        ]

        for score in scores:
            high_score_manager.submit_score(score)

        # Get personal best
        pb = high_score_manager.get_personal_best("Player1", "pool", "danger", "normal")
        assert pb is not None
        assert pb.score == 1500

        # Non-existent player
        no_pb = high_score_manager.get_personal_best(
            "Player3", "pool", "danger", "normal"
        )
        assert no_pb is None

    def test_get_statistics(self, high_score_manager):
        """Test getting statistics for a game mode."""
        # Add variety of scores
        scores = [
            ScoreEntry(
                "Player1", 1000, "danger", "pool", "normal", datetime.now(), 60.0
            ),
            ScoreEntry(
                "Player2", 1500, "danger", "pool", "normal", datetime.now(), 55.0
            ),
            ScoreEntry(
                "Player3", 2000, "danger", "pool", "normal", datetime.now(), 50.0
            ),
            ScoreEntry(
                "Player4", 800, "danger", "pool", "normal", datetime.now(), 65.0
            ),
        ]

        for score in scores:
            high_score_manager.submit_score(score)

        stats = high_score_manager.get_statistics("pool", "danger", "normal")

        assert stats["total_games"] == 4
        assert stats["average_score"] == 1325.0
        assert stats["top_score"] == 2000
        assert stats["top_player"] == "Player3"

    def test_export_import_leaderboard(self, high_score_manager):
        """Test exporting and importing leaderboard data."""
        # Add some scores
        scores = [
            ScoreEntry(
                "Player1", 1500, "danger", "pool", "normal", datetime.now(), 55.0
            ),
            ScoreEntry(
                "Player2", 1200, "danger", "pool", "normal", datetime.now(), 60.0
            ),
        ]

        for score in scores:
            high_score_manager.submit_score(score)

        # Export
        export_data = high_score_manager.export_leaderboard("pool", "danger", "normal")

        assert len(export_data) == 2
        assert export_data[0]["player_name"] == "Player1"
        assert export_data[0]["score"] == 1500

        # Clear and import
        high_score_manager.clear_scores("pool", "danger", "normal")
        high_score_manager.import_leaderboard("pool", "danger", "normal", export_data)

        # Verify import
        imported = high_score_manager.get_leaderboard("pool", "danger", "normal")
        assert len(imported) == 2
        assert imported[0].player_name == "Player1"

    def test_vegas_combined_scoring(self, high_score_manager):
        """Test Vegas game combined scoring (points + time bonus)."""
        # Vegas uses combined scoring
        entry = ScoreEntry(
            player_name="VegasPlayer",
            score=5000,  # Base points
            character="danger",
            game_mode="vegas",
            difficulty="normal",
            date=datetime.now(),
            time_elapsed=120.0,  # 2 minutes
            combo_multiplier=1.5,
        )

        # Calculate final score (base * combo + time bonus)
        final_score = high_score_manager._calculate_vegas_score(entry)
        expected = 5000 * 1.5 + (300 - 120) * 10  # Base * combo + time bonus

        assert final_score == expected

    def test_score_validation(self, high_score_manager):
        """Test score validation for different game modes."""
        # Invalid game mode
        with pytest.raises(ValueError):
            entry = ScoreEntry(
                "Player", 1000, "danger", "invalid_game", "normal", datetime.now(), 60.0
            )
            high_score_manager.submit_score(entry)

        # Invalid character
        with pytest.raises(ValueError):
            entry = ScoreEntry(
                "Player", 1000, "invalid_char", "pool", "normal", datetime.now(), 60.0
            )
            high_score_manager.submit_score(entry)

        # Invalid difficulty
        with pytest.raises(ValueError):
            entry = ScoreEntry(
                "Player", 1000, "danger", "pool", "super_hard", datetime.now(), 60.0
            )
            high_score_manager.submit_score(entry)
