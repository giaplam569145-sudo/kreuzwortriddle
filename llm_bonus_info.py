#!/usr/bin/env python3
"""LLM information for the bonus word reveal feature.

This file contains specific information for LLMs:
- Which letters are available for the bonus word.
- A maximum of one bonus word letter per word is possible.
- The maximum length of the bonus word is based on the number of words.
- Progressive reveal mechanism.

Author: Qwen Code (2025)
"""

from typing import Dict, List, Set, Tuple, Any, Optional


class LLMBonusInfo:
    """Specialized information class for LLMs.

    Usage:
    1. The LLM receives information about available letters.
    2. The LLM can understand the bonus word logic.
    3. The LLM can control the progressive reveal.
    """

    def __init__(self):
        """Initializes the LLMBonusInfo."""
        self.available_letters: Set[str] = set()
        self.max_bonus_length: int = 0
        self.revealed_letters: List[str] = []
        self.bonus_word: str = ""

    def update_bonus_info(self, current_grid: List[List[str]]) -> None:
        """Updates the information about available letters for the bonus word.

        Args:
            current_grid: The current grid with placed words.
        """
        self.available_letters.clear()

        # Sammle alle Buchstaben aus dem Gitter
        for row in current_grid:
            for cell in row:
                if cell and cell.isalpha():
                    self.available_letters.add(cell.upper())

    def get_available_letters(self) -> Set[str]:
        """Returns the currently available letters for the bonus word.

        Returns:
            A set of available letters.
        """
        return self.available_letters.copy()

    def check_bonus_reveal_conditions(self) -> bool:
        """Checks the conditions for revealing new letters.

        Returns:
            True if the conditions are met, False otherwise.
        """
        return (len(self.available_letters) > 0 and
                len(self.revealed_letters) < len(self.bonus_word))

    def can_reveal_new_letter(self) -> bool:
        """Checks if a new letter of the bonus word can be revealed.

        Returns:
            True if a new letter can be revealed.
        """
        if not self.bonus_word:
            return False

        # Finde den nächsten nicht aufgedeckten Buchstaben
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                return letter in self.available_letters

        return False

    def set_bonus_word(self, word: str) -> None:
        """Sets the bonus word and initializes the reveal process.

        Args:
            word: The bonus word.
        """
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)
        self.max_bonus_length = len(word)

    def reveal_next_letter(self) -> Optional[str]:
        """Reveals the next available letter.

        Returns:
            The revealed letter or None.
        """
        if not self.can_reveal_new_letter():
            return None

        # Finde den nächsten aufdeckbaren Buchstaben
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                if letter in self.available_letters:
                    if i < len(self.revealed_letters):
                        self.revealed_letters[i] = letter
                    else:
                        self.revealed_letters.append(letter)
                    return letter

        return None

    def get_bonus_word_hint(self) -> str:
        """Returns a hint for the bonus word.

        Returns:
            A string with the current state of the bonus word.
        """
        if not self.bonus_word:
            return "Kein Bonuswort gesetzt"

        revealed = ''.join(self.revealed_letters)
        return f"Bonuswort: {revealed} ({len([l for l in self.revealed_letters if l != '_'])}/{len(self.bonus_word)} Buchstaben)"

    def get_bonus_statistics(self) -> Dict[str, Any]:
        """Returns statistics about the bonus word.

        Returns:
            A dictionary with statistics.
        """
        return {
            "bonus_word": self.bonus_word,
            "bonus_word_length": len(self.bonus_word),
            "available_letters": list(self.available_letters),
            "revealed_letters": self.revealed_letters,
            "revealed_count": len([l for l in self.revealed_letters if l != '_']),
            "can_reveal_more": self.can_reveal_new_letter(),
            "completion_percentage": (len([l for l in self.revealed_letters if l != '_']) / len(self.bonus_word) * 100) if self.bonus_word else 0
        }


# LLM-SPEZIFISCHE INFORMATIONEN
class BonusWordConstraints:
    """Defines the constraints for the bonus word."""

    def __init__(self):
        """Initializes the BonusWordConstraints."""
        self.max_letters_per_word: int = 1
        self.max_bonus_length: int = 8  # Standard-Maximallänge
        self.min_bonus_length: int = 3

    def get_constraints_info(self) -> Dict[str, Any]:
        """Returns information about the maximum possible length of the bonus
        word.

        Returns:
            A dictionary with constraint information.
        """
        return {
            "max_letters_per_word": self.max_letters_per_word,
            "max_bonus_length": self.max_bonus_length,
            "min_bonus_length": self.min_bonus_length,
            "description": "Maximal ein Buchstabe pro Wort für das Bonuswort"
        }

    def calculate_max_bonus_length(self, num_questions: int) -> int:
        """Calculates the maximum length of the bonus word based on the
        number of questions.

        Args:
            num_questions: The number of questions in the puzzle.

        Returns:
            The maximum length of the bonus word.
        """
        calculated = min(num_questions * self.max_letters_per_word, self.max_bonus_length)
        return max(calculated, self.min_bonus_length)

    def validate_bonus_word(self, bonus_word: str, available_letters: Set[str]) -> List[str]:
        """Validates a bonus word against the available letters.

        Args:
            bonus_word: The bonus word to validate.
            available_letters: The available letters.

        Returns:
            A list of validation errors.
        """
        errors = []

        if not bonus_word.strip():
            errors.append("Bonuswort ist leer")
            return errors

        if len(bonus_word) < self.min_bonus_length:
            errors.append(f"Bonuswort ist zu kurz (mindestens {self.min_bonus_length} Buchstaben)")

        if len(bonus_word) > self.max_bonus_length:
            errors.append(f"Bonuswort ist zu lang (maximal {self.max_bonus_length} Buchstaben)")

        if not bonus_word.isalpha():
            errors.append("Bonuswort darf nur Buchstaben enthalten")

        # Prüfe ob alle Buchstaben verfügbar sind
        word_letters = set(bonus_word.upper())
        missing_letters = word_letters - available_letters

        if missing_letters:
            errors.append(f"Fehlende Buchstaben im Gitter: {', '.join(missing_letters)}")

        return errors


def get_bonus_word_guidelines() -> Dict[str, Any]:
    """Provides the LLM with clear guidelines for the bonus word.

    Returns:
        A dictionary with guidelines.
    """
    return {
        "purpose": "Das Bonuswort ergibt sich aus den Kreuzungspunkten der anderen Wörter",
        "constraints": {
            "max_letters_per_word": "Maximal ein Bonuswortbuchstabe pro Wort",
            "max_total_length": "Maximal 8 Buchstaben für das gesamte Bonuswort",
            "min_total_length": "Mindestens 3 Buchstaben für das Bonuswort"
        },
        "mechanism": {
            "progressive_reveal": "Das Bonuswort wird Buchstabe für Buchstabe aufgedeckt",
            "crossing_points": "Buchstaben stammen aus den Kreuzungspunkten der Wörter",
            "llm_role": "LLM identifiziert das Bonuswort wenn genug Buchstaben bekannt sind"
        },
        "examples": [
            {
                "words": ["Berlin", "Paris", "Rom"],
                "bonus_word": "EUROPA",
                "explanation": "Alle Hauptstädte gehören zum gleichen Kontinent"
            }
        ]
    }


# BEISPIEL FÜR LLMs
if __name__ == "__main__":
    """
    Example for LLM information about the bonus word.
    """
    # Erstelle Bonus-Info-System
    bonus_info = LLMBonusInfo()
    constraints = BonusWordConstraints()

    # Beispiel-Gitter
    example_grid = [
        ['B', 'E', 'R', 'L', 'I', 'N'],
        ['E', '.', '.', '.', '.', '.'],
        ['R', '.', 'P', 'A', 'R', 'I'],
        ['L', '.', '.', '.', '.', 'S'],
        ['I', '.', '.', '.', '.', '.'],
        ['N', '.', '.', '.', '.', '.']
    ]

    # Aktualisiere verfügbare Buchstaben
    bonus_info.update_bonus_info(example_grid)

    # Setze Bonuswort
    bonus_info.set_bonus_word("EUROPA")

    print("=== BONUSWORT-INFORMATIONEN FÜR LLMs ===\n")

    print(f"Verfügbare Buchstaben: {bonus_info.get_available_letters()}")
    print(f"Bonuswort-Hinweis: {bonus_info.get_bonus_word_hint()}")
    print(f"Kann Buchstabe aufdecken: {bonus_info.can_reveal_new_letter()}")

    # Decke Buchstaben auf
    for i in range(3):
        letter = bonus_info.reveal_next_letter()
        if letter:
            print(f"Buchstabe aufgedeckt: {letter}")
            print(f"Status: {bonus_info.get_bonus_word_hint()}")

    print(f"\nStatistiken: {bonus_info.get_bonus_statistics()}")
    print(f"\nRichtlinien: {get_bonus_word_guidelines()}")
