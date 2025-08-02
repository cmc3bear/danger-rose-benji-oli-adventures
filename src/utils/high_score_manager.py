"""High score tracking and leaderboard management for Danger Rose game."""

import logging
from dataclasses import asdict, dataclass
from datetime import datetime
from enum import Enum
from typing import Any

from src.utils.save_manager import SaveManager

logger = logging.getLogger(__name__)


class ScoreType(Enum):
    """Types of scoring systems for different games."""

    TIME_BASED = "time"  # Lower is better (ski)
    POINTS_BASED = "points"  # Higher is better (pool)
    COMBINED = "combined"  # Points + time bonus (vegas)


@dataclass
class ScoreEntry:
    """Represents a single high score entry."""

    player_name: str
    score: float
    character: str
    game_mode: str
    difficulty: str
    date: datetime
    time_elapsed: float
    combo_multiplier: float = 1.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        data = asdict(self)
        data["date"] = self.date.isoformat()
        return data

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "ScoreEntry":
        """Create from dictionary."""
        data = data.copy()
        data["date"] = datetime.fromisoformat(data["date"])
        return cls(**data)


class HighScoreManager:
    """Manages high scores across all game modes with advanced features."""

    # Game configuration
    GAME_MODES = ["ski", "pool", "vegas"]
    CHARACTERS = ["danger", "rose", "dad"]
    DIFFICULTIES = ["easy", "normal", "hard"]

    # Scoring system per game
    SCORE_TYPES = {
        "ski": ScoreType.TIME_BASED,
        "pool": ScoreType.POINTS_BASED,
        "vegas": ScoreType.COMBINED,
    }

    # Maximum scores to keep per category
    MAX_SCORES_PER_CATEGORY = 10

    def __init__(self, save_manager: SaveManager | None = None):
        """Initialize HighScoreManager.

        Args:
            save_manager: SaveManager instance. Creates new one if not provided.
        """
        self.save_manager = save_manager or SaveManager()
        self._ensure_score_structure()

    def _ensure_score_structure(self) -> None:
        """Ensure the save data has proper score structure."""
        if self.save_manager._current_save_data is None:
            self.save_manager.load()

        # Ensure high_scores exists with all difficulties
        if "high_scores" not in self.save_manager._current_save_data:
            self.save_manager._current_save_data["high_scores"] = {}

        scores = self.save_manager._current_save_data["high_scores"]

        # Ensure all game modes and characters exist with difficulty levels
        for game in self.GAME_MODES:
            if game not in scores:
                scores[game] = {}
            for character in self.CHARACTERS:
                if character not in scores[game]:
                    scores[game][character] = {}
                elif isinstance(scores[game][character], list):
                    # Migration: convert old list format to new difficulty-based format
                    old_scores = scores[game][character]
                    scores[game][character] = {
                        "easy": [],
                        "normal": old_scores,  # Assume old scores were normal difficulty
                        "hard": [],
                    }

                # Ensure it's a dict and has all difficulty levels
                if isinstance(scores[game][character], dict):
                    for difficulty in self.DIFFICULTIES:
                        if difficulty not in scores[game][character]:
                            scores[game][character][difficulty] = []

    def submit_score(self, entry: ScoreEntry) -> bool:
        """Submit a new score and check if it's a high score.

        Args:
            entry: ScoreEntry to submit

        Returns:
            True if score made it to the leaderboard

        Raises:
            ValueError: If game mode, character, or difficulty is invalid
        """
        # Validate input
        if entry.game_mode not in self.GAME_MODES:
            raise ValueError(f"Invalid game mode: {entry.game_mode}")
        if entry.character not in self.CHARACTERS:
            raise ValueError(f"Invalid character: {entry.character}")
        if entry.difficulty not in self.DIFFICULTIES:
            raise ValueError(f"Invalid difficulty: {entry.difficulty}")

        # Calculate final score for Vegas
        if entry.game_mode == "vegas":
            entry.score = self._calculate_vegas_score(entry)

        # Get current scores
        scores = self._get_score_list(
            entry.game_mode, entry.character, entry.difficulty
        )

        # Add new score
        scores.append(entry.to_dict())

        # Sort based on game type
        scores = self._sort_scores(scores, entry.game_mode)

        # Keep only top scores
        scores = scores[: self.MAX_SCORES_PER_CATEGORY]

        # Update save data
        self._set_score_list(entry.game_mode, entry.character, entry.difficulty, scores)

        # Save to disk
        self.save_manager.save()

        # Check if score made the leaderboard
        score_dicts = [
            s
            for s in scores
            if s["player_name"] == entry.player_name and s["score"] == entry.score
        ]
        is_high_score = len(score_dicts) > 0

        if is_high_score:
            logger.info(
                f"New high score! {entry.player_name}: {entry.score} in {entry.game_mode}"
            )

        return is_high_score

    def get_leaderboard(
        self, game_mode: str, character: str, difficulty: str | None = None
    ) -> list[ScoreEntry]:
        """Get leaderboard for specific category.

        Args:
            game_mode: Game mode (ski, pool, vegas)
            character: Character name
            difficulty: Difficulty level. If None, returns all difficulties combined

        Returns:
            List of ScoreEntry objects sorted by rank
        """
        if difficulty:
            scores = self._get_score_list(game_mode, character, difficulty)
            return [ScoreEntry.from_dict(s) for s in scores]

        # Combine all difficulties
        all_scores = []
        for diff in self.DIFFICULTIES:
            scores = self._get_score_list(game_mode, character, diff)
            all_scores.extend(scores)

        # Sort combined scores
        all_scores = self._sort_scores(all_scores, game_mode)

        return [
            ScoreEntry.from_dict(s) for s in all_scores[: self.MAX_SCORES_PER_CATEGORY]
        ]

    def is_high_score(
        self, score: float, game_mode: str, character: str, difficulty: str
    ) -> bool:
        """Check if a score would make the leaderboard.

        Args:
            score: Score to check
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level

        Returns:
            True if score would make the leaderboard
        """
        scores = self._get_score_list(game_mode, character, difficulty)

        if len(scores) < self.MAX_SCORES_PER_CATEGORY:
            return True

        # Check based on game type
        score_type = self.SCORE_TYPES[game_mode]

        if score_type == ScoreType.TIME_BASED:
            # Lower is better
            worst_score = max(s["score"] for s in scores)
            return score < worst_score
        # Higher is better
        worst_score = min(s["score"] for s in scores)
        return score > worst_score

    def get_rank(
        self, score: float, game_mode: str, character: str, difficulty: str
    ) -> int:
        """Get the rank a score would achieve.

        Args:
            score: Score to check
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level

        Returns:
            Rank (1-based) the score would achieve
        """
        scores = self._get_score_list(game_mode, character, difficulty)
        score_values = [s["score"] for s in scores]

        score_type = self.SCORE_TYPES[game_mode]
        rank = 1

        for existing_score in score_values:
            if score_type == ScoreType.TIME_BASED:
                if score >= existing_score:
                    rank += 1
            elif score <= existing_score:
                rank += 1

        return rank

    def get_personal_best(
        self, player_name: str, game_mode: str, character: str, difficulty: str
    ) -> ScoreEntry | None:
        """Get personal best score for a player.

        Args:
            player_name: Player name
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level

        Returns:
            Best ScoreEntry for player or None
        """
        scores = self._get_score_list(game_mode, character, difficulty)
        player_scores = [s for s in scores if s["player_name"] == player_name]

        if not player_scores:
            return None

        # Return first (best) score
        return ScoreEntry.from_dict(player_scores[0])

    def clear_scores(self, game_mode: str, character: str, difficulty: str) -> None:
        """Clear scores for specific category.

        Args:
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level
        """
        self._set_score_list(game_mode, character, difficulty, [])
        self.save_manager.save()
        logger.info(f"Cleared scores for {game_mode}/{character}/{difficulty}")

    def get_statistics(
        self, game_mode: str, character: str, difficulty: str
    ) -> dict[str, Any]:
        """Get statistics for a category.

        Args:
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level

        Returns:
            Dictionary with statistics
        """
        scores = self._get_score_list(game_mode, character, difficulty)

        if not scores:
            return {
                "total_games": 0,
                "average_score": 0,
                "top_score": None,
                "top_player": None,
            }

        score_values = [s["score"] for s in scores]

        return {
            "total_games": len(scores),
            "average_score": sum(score_values) / len(score_values),
            "top_score": scores[0]["score"],
            "top_player": scores[0]["player_name"],
        }

    def export_leaderboard(
        self, game_mode: str, character: str, difficulty: str
    ) -> list[dict[str, Any]]:
        """Export leaderboard data for external use.

        Args:
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level

        Returns:
            List of score dictionaries
        """
        return self._get_score_list(game_mode, character, difficulty)

    def import_leaderboard(
        self,
        game_mode: str,
        character: str,
        difficulty: str,
        scores: list[dict[str, Any]],
    ) -> None:
        """Import leaderboard data.

        Args:
            game_mode: Game mode
            character: Character name
            difficulty: Difficulty level
            scores: List of score dictionaries to import
        """
        # Validate and convert
        valid_scores = []
        for score_dict in scores:
            try:
                ScoreEntry.from_dict(score_dict)  # Validate structure
                valid_scores.append(score_dict)
            except Exception as e:
                logger.warning(f"Skipping invalid score entry: {e}")

        # Sort and limit
        valid_scores = self._sort_scores(valid_scores, game_mode)
        valid_scores = valid_scores[: self.MAX_SCORES_PER_CATEGORY]

        self._set_score_list(game_mode, character, difficulty, valid_scores)
        self.save_manager.save()
        logger.info(f"Imported {len(valid_scores)} scores")

    def _calculate_vegas_score(self, entry: ScoreEntry) -> float:
        """Calculate Vegas combined score.

        Vegas scoring: base_points * combo_multiplier + time_bonus
        Time bonus: (300 - time_elapsed) * 10 (max 5 minutes)

        Args:
            entry: ScoreEntry with base score

        Returns:
            Final calculated score
        """
        base_score = entry.score * entry.combo_multiplier

        # Time bonus (max 300 seconds / 5 minutes)
        time_limit = 300
        time_bonus = max(0, (time_limit - entry.time_elapsed) * 10)

        return base_score + time_bonus

    def _get_score_list(
        self, game_mode: str, character: str, difficulty: str
    ) -> list[dict[str, Any]]:
        """Get score list for specific category."""
        return (
            self.save_manager._current_save_data.get("high_scores", {})
            .get(game_mode, {})
            .get(character, {})
            .get(difficulty, [])
        )

    def _set_score_list(
        self,
        game_mode: str,
        character: str,
        difficulty: str,
        scores: list[dict[str, Any]],
    ) -> None:
        """Set score list for specific category."""
        self._ensure_score_structure()
        self.save_manager._current_save_data["high_scores"][game_mode][character][
            difficulty
        ] = scores

    def _sort_scores(
        self, scores: list[dict[str, Any]], game_mode: str
    ) -> list[dict[str, Any]]:
        """Sort scores based on game type.

        Args:
            scores: List of score dictionaries
            game_mode: Game mode to determine sort order

        Returns:
            Sorted list of scores
        """
        score_type = self.SCORE_TYPES[game_mode]

        if score_type == ScoreType.TIME_BASED:
            # Lower is better
            return sorted(scores, key=lambda x: x["score"])
        # Higher is better (POINTS_BASED and COMBINED)
        return sorted(scores, key=lambda x: x["score"], reverse=True)
