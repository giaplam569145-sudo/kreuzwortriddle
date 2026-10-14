from typing import List, Set, Optional, Dict, Any

class BonusSystem:
    """Manages the bonus word logic for the crossword puzzle.

    Handles setting the bonus word, revealing letters based on the grid state,
    and providing hints.
    """

    def __init__(self):
        self.bonus_word: str = ""
        self.revealed_letters: List[str] = []

    def set_bonus_word(self, word: str) -> None:
        """Sets the bonus word.

        Args:
            word: The bonus word.
        """
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)

    def get_available_letters(self, grid: List[List[str]]) -> Set[str]:
        """Gets the set of available letters from the grid.

        Args:
            grid: The current state of the crossword grid.

        Returns:
            A set of strings, where each string is an available letter.
        """
        available = set()
        for row in grid:
            for cell in row:
                if cell and cell.strip():
                    available.add(cell.upper())
        return available

    def can_reveal_bonus_letter(self, grid: List[List[str]]) -> bool:
        """Checks if a new letter of the bonus word can be revealed.

        Args:
            grid: The current state of the crossword grid.

        Returns:
            True if a new letter can be revealed, False otherwise.
        """
        if not self.bonus_word:
            return False

        available_letters = self.get_available_letters(grid)
        return '_' in self.revealed_letters and any(
            letter in available_letters and self.revealed_letters[i] == '_'
            for i, letter in enumerate(self.bonus_word)
        )

    def reveal_next_letter(self, grid: List[List[str]]) -> Optional[str]:
        """Reveals the next letter of the bonus word if available in the grid.

        Args:
            grid: The current state of the crossword grid.

        Returns:
            The revealed letter, or None if no letter can be revealed.
        """
        if not self.can_reveal_bonus_letter(grid):
            return None

        available_letters = self.get_available_letters(grid)
        for i, letter in enumerate(self.bonus_word):
            if self.revealed_letters[i] == '_' and letter in available_letters:
                self.revealed_letters[i] = letter
                return letter

        return None

    def get_bonus_word_hint(self) -> str:
        """Provides a hint for the bonus word.

        Returns:
            A string with the current state of the bonus word.
        """
        if not self.bonus_word:
            return "No bonus word set"

        return f"Bonus word: {''.join(self.revealed_letters)}"

    def get_status(self) -> Dict[str, Any]:
        """Returns the status of the bonus system."""
        return {
            "bonus_word_set": bool(self.bonus_word),
            "revealed_count": len([l for l in self.revealed_letters if l != '_']),
            "total_length": len(self.bonus_word) if self.bonus_word else 0,
            "hint": self.get_bonus_word_hint()
        }
