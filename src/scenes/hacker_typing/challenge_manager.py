"""Challenge content manager for the Hacker Typing Challenge."""

import json
import os
import random
from typing import List, Dict, Optional
from dataclasses import dataclass
from enum import Enum


class ChallengeType(Enum):
    """Types of typing challenges."""
    PASSWORD = "password"
    COMMAND = "command"
    CODE_SNIPPET = "code_snippet"
    FULL_SCRIPT = "full_script"


@dataclass
class Challenge:
    """Single typing challenge."""
    id: str
    name: str
    type: ChallengeType
    text: str
    difficulty: int  # 1-4
    wpm_target: float
    accuracy_target: float
    time_limit: float
    description: str
    hints: List[str]
    
    @property
    def char_count(self) -> int:
        return len(self.text)
    
    @property
    def word_count(self) -> int:
        return self.char_count // 5  # Standard typing metric


class ChallengeManager:
    """Manages loading and progression of typing challenges."""
    
    # Default challenges if content files don't exist
    DEFAULT_CHALLENGES = {
        ChallengeType.PASSWORD: [
            {
                "id": "pass_1",
                "name": "Basic Password",
                "text": "admin123",
                "difficulty": 1,
                "wpm_target": 15,
                "accuracy_target": 80,
                "time_limit": 30,
                "description": "Crack a simple password",
                "hints": ["Common admin password", "Numbers follow letters"]
            },
            {
                "id": "pass_2",
                "name": "Complex Password",
                "text": "P@ssw0rd!2024",
                "difficulty": 1,
                "wpm_target": 15,
                "accuracy_target": 85,
                "time_limit": 30,
                "description": "Crack a password with special characters",
                "hints": ["Contains symbols", "Mix of cases"]
            }
        ],
        ChallengeType.COMMAND: [
            {
                "id": "cmd_1",
                "name": "List Files",
                "text": "ls -la /home/user/",
                "difficulty": 2,
                "wpm_target": 25,
                "accuracy_target": 85,
                "time_limit": 45,
                "description": "List all files in a directory",
                "hints": ["Unix command", "Shows hidden files"]
            },
            {
                "id": "cmd_2",
                "name": "Network Scan",
                "text": "nmap -sS -p 1-1000 192.168.1.1",
                "difficulty": 2,
                "wpm_target": 25,
                "accuracy_target": 85,
                "time_limit": 45,
                "description": "Perform a stealth port scan",
                "hints": ["Network mapping tool", "Stealth SYN scan"]
            }
        ],
        ChallengeType.CODE_SNIPPET: [
            {
                "id": "code_1",
                "name": "Python Import",
                "text": "import socket\ns = socket.socket(socket.AF_INET, socket.SOCK_STREAM)",
                "difficulty": 3,
                "wpm_target": 30,
                "accuracy_target": 90,
                "time_limit": 60,
                "description": "Create a network socket in Python",
                "hints": ["Python networking", "TCP socket creation"]
            },
            {
                "id": "code_2",
                "name": "SQL Injection",
                "text": "SELECT * FROM users WHERE username = 'admin' OR '1'='1'",
                "difficulty": 3,
                "wpm_target": 30,
                "accuracy_target": 90,
                "time_limit": 60,
                "description": "Classic SQL injection pattern",
                "hints": ["Database exploit", "Always true condition"]
            }
        ],
        ChallengeType.FULL_SCRIPT: [
            {
                "id": "script_1",
                "name": "Port Scanner",
                "text": "#!/usr/bin/python3\nimport socket\nimport sys\n\nfor port in range(1, 1025):\n    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)\n    result = sock.connect_ex(('127.0.0.1', port))\n    if result == 0:\n        print(f'Port {port}: Open')\n    sock.close()",
                "difficulty": 4,
                "wpm_target": 40,
                "accuracy_target": 95,
                "time_limit": 120,
                "description": "Complete port scanning script",
                "hints": ["Python script", "Scans first 1024 ports"]
            }
        ]
    }
    
    def __init__(self, content_path: Optional[str] = None):
        self.content_path = content_path or "src/content/hacker_challenges"
        self.challenges: Dict[ChallengeType, List[Challenge]] = {}
        self.completed_challenges: set = set()
        self.current_level = 1
        self.load_challenges()
    
    def load_challenges(self):
        """Load challenges from files or use defaults."""
        # Try to load from JSON files
        if os.path.exists(self.content_path):
            for challenge_type in ChallengeType:
                filename = f"level_{challenge_type.value}.json"
                filepath = os.path.join(self.content_path, filename)
                
                if os.path.exists(filepath):
                    try:
                        with open(filepath, 'r') as f:
                            data = json.load(f)
                            self.challenges[challenge_type] = [
                                Challenge(
                                    type=challenge_type,
                                    **challenge_data
                                )
                                for challenge_data in data
                            ]
                    except Exception as e:
                        print(f"Error loading {filepath}: {e}")
                        self._load_default_challenges(challenge_type)
                else:
                    self._load_default_challenges(challenge_type)
        else:
            # Load all defaults
            for challenge_type in ChallengeType:
                self._load_default_challenges(challenge_type)
    
    def _load_default_challenges(self, challenge_type: ChallengeType):
        """Load default challenges for a specific type."""
        if challenge_type in self.DEFAULT_CHALLENGES:
            self.challenges[challenge_type] = [
                Challenge(
                    type=challenge_type,
                    **challenge_data
                )
                for challenge_data in self.DEFAULT_CHALLENGES[challenge_type]
            ]
        else:
            self.challenges[challenge_type] = []
    
    def get_challenges_by_level(self, level: int) -> List[Challenge]:
        """Get all challenges for a specific difficulty level."""
        level_challenges = []
        for challenge_list in self.challenges.values():
            level_challenges.extend([c for c in challenge_list if c.difficulty == level])
        return level_challenges
    
    def get_challenge_by_id(self, challenge_id: str) -> Optional[Challenge]:
        """Get a specific challenge by ID."""
        for challenge_list in self.challenges.values():
            for challenge in challenge_list:
                if challenge.id == challenge_id:
                    return challenge
        return None
    
    def get_random_challenge(self, challenge_type: Optional[ChallengeType] = None,
                           difficulty: Optional[int] = None) -> Optional[Challenge]:
        """Get a random challenge matching criteria."""
        available_challenges = []
        
        if challenge_type:
            challenge_lists = [self.challenges.get(challenge_type, [])]
        else:
            challenge_lists = self.challenges.values()
        
        for challenge_list in challenge_lists:
            for challenge in challenge_list:
                if challenge.id not in self.completed_challenges:
                    if difficulty is None or challenge.difficulty == difficulty:
                        available_challenges.append(challenge)
        
        return random.choice(available_challenges) if available_challenges else None
    
    def mark_completed(self, challenge_id: str):
        """Mark a challenge as completed."""
        self.completed_challenges.add(challenge_id)
    
    def get_level_progress(self, level: int) -> Dict[str, any]:
        """Get progress for a specific level."""
        level_challenges = self.get_challenges_by_level(level)
        completed = [c for c in level_challenges if c.id in self.completed_challenges]
        
        return {
            "total": len(level_challenges),
            "completed": len(completed),
            "percentage": (len(completed) / len(level_challenges) * 100) if level_challenges else 0,
            "remaining": len(level_challenges) - len(completed)
        }
    
    def unlock_next_level(self) -> bool:
        """Check if next level should be unlocked."""
        current_progress = self.get_level_progress(self.current_level)
        
        # Unlock next level at 80% completion
        if current_progress["percentage"] >= 80 and self.current_level < 4:
            self.current_level += 1
            return True
        return False
    
    def get_campaign_challenges(self) -> List[Challenge]:
        """Get a curated list of challenges for campaign mode."""
        campaign = []
        
        # Level 1: Passwords (2 challenges)
        passwords = self.challenges.get(ChallengeType.PASSWORD, [])[:2]
        campaign.extend(passwords)
        
        # Level 2: Commands (3 challenges)
        commands = self.challenges.get(ChallengeType.COMMAND, [])[:3]
        campaign.extend(commands)
        
        # Level 3: Code snippets (3 challenges)
        snippets = self.challenges.get(ChallengeType.CODE_SNIPPET, [])[:3]
        campaign.extend(snippets)
        
        # Level 4: Full scripts (2 challenges)
        scripts = self.challenges.get(ChallengeType.FULL_SCRIPT, [])[:2]
        campaign.extend(scripts)
        
        return campaign