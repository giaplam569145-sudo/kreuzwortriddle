#!/usr/bin/env python3
"""Kreuzwort-Riddle Framework für LLMs.

Ein Python-Framework zur automatischen Erstellung von Kreuzworträtseln.
Für LLMs geschrieben - konzentriert sich auf Fragen/Antworten, nicht auf Logik.

Autor: Qwen Code (2025)
"""

import json
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import random


class Orientation(Enum):
    """Enumeration for word orientation in the grid.

    Attributes:
        HORIZONTAL: Represents horizontal orientation.
        VERTICAL: Represents vertical orientation.
    """
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class Question:
    """Represents a single crossword question with validation logic.

    Attributes:
        question_text: The text of the question.
        answer: The answer to the question.
        number: The number of the question in the crossword.
        orientation: The orientation of the answer in the grid.
    """
    question_text: str
    answer: str
    number: int = 0
    orientation: Orientation = Orientation.HORIZONTAL

    def validate(self) -> List[str]:
        """Validates the question and returns a list of errors.

        Returns:
            A list of strings, where each string is an error message.
        """
        errors = []

        if not self.question_text.strip():
            errors.append("Frage-Text ist leer")
        if not self.answer.strip():
            errors.append("Antwort ist leer")
        if len(self.answer) < 2:
            errors.append("Antwort muss mindestens 2 Buchstaben lang sein")
        if not self.answer.isalpha():
            errors.append("Antwort darf nur Buchstaben enthalten")
        if len(self.answer) > 20:
            errors.append("Antwort ist zu lang (max 20 Buchstaben)")

        return errors


class ValidationError(Exception):
    """Custom exception for validation problems.

    Attributes:
        message: The error message.
        problematic_questions: A list of tuples, where each tuple contains
            the question number and the error message.
    """
    def __init__(self, message: str, problematic_questions: List[Tuple[int, str]] = None):
        self.message = message
        self.problematic_questions = problematic_questions or []
        super().__init__(self.message)


@dataclass
class WordPlacement:
    """Represents the position of a word in the grid.

    Attributes:
        question: The Question object associated with this placement.
        x: The x-coordinate of the starting letter.
        y: The y-coordinate of the starting letter.
        length: The length of the word.
    """
    question: Question
    x: int
    y: int
    length: int

    def overlaps_with(self, other: 'WordPlacement') -> bool:
        """Checks if this word placement overlaps with another.

        Args:
            other: The other WordPlacement object to check against.

        Returns:
            True if the words overlap, False otherwise.
        """
        if self.question.orientation == other.question.orientation:
            return False

        # Prüfe ob sich die Wörter kreuzen
        if self.question.orientation == Orientation.HORIZONTAL:
            # Horizontales Wort kreuzt vertikales Wort
            return (self.x <= other.x <= self.x + self.length - 1 and
                    other.y <= self.y <= other.y + other.length - 1)
        else:
            # Vertikales Wort kreuzt horizontales Wort
            return (other.x <= self.x <= other.x + other.length - 1 and
                    self.y <= other.y <= self.y + other.length - 1)


class KreuzwortRiddle:
    """Main class for creating the crossword puzzle.

    Attributes:
        width: The width of the crossword grid.
        height: The height of the crossword grid.
        questions: A list of Question objects.
        placements: A list of WordPlacement objects.
        grid: A 2D list representing the crossword grid.
    """

    def __init__(self, width: int = 15, height: int = 15):
        """Initializes the KreuzwortRiddle.

        Args:
            width: The width of the crossword grid.
            height: The height of the crossword grid.
        """
        self.width = width
        self.height = height
        self.questions: List[Question] = []
        self.placements: List[WordPlacement] = []
        self.grid: List[List[str]] = [['' for _ in range(width)] for _ in range(height)]

    def add_question(self, question: str, answer: str, orientation: Orientation = Orientation.HORIZONTAL) -> None:
        """Adds a question with automatic validation.

        Args:
            question: The text of the question.
            answer: The answer to the question.
            orientation: The orientation of the word in the grid.

        Raises:
            ValidationError: If the question is invalid.
        """
        new_question = Question(question, answer, len(self.questions) + 1, orientation)
        errors = new_question.validate()

        if errors:
            raise ValidationError(
                f"Frage {len(self.questions) + 1} ist ungültig: {', '.join(errors)}",
                [(len(self.questions) + 1, error) for error in errors]
            )

        self.questions.append(new_question)

    def validate_all_questions(self) -> List[str]:
        """Validates all questions and returns a list of errors.

        Returns:
            A list of strings, where each string is an error message.
        """
        all_errors = []

        for i, question in enumerate(self.questions, 1):
            errors = question.validate()
            if errors:
                all_errors.extend([f"Frage {i}: {error}" for error in errors])

        return all_errors

    def generate_grid(self) -> bool:
        """Tries to generate the crossword puzzle grid.

        Returns:
            True if the grid was generated successfully, False otherwise.
        """
        if not self.questions:
            return False

        # Einfache Platzierungsstrategie
        self.placements.clear()
        self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]

        # Platziere erste Frage in der Mitte
        first_question = self.questions[0]
        start_x = (self.width - len(first_question.answer)) // 2
        start_y = self.height // 2

        placement = WordPlacement(
            question=first_question,
            x=start_x,
            y=start_y,
            length=len(first_question.answer)
        )
        self.placements.append(placement)

        # Platziere Wort im Gitter
        for i, char in enumerate(first_question.answer):
            self.grid[start_y][start_x + i] = char.upper()

        # Versuche andere Wörter zu platzieren
        for question in self.questions[1:]:
            placed = False
            for existing_placement in self.placements:
                if self._try_place_word(question, existing_placement):
                    placed = True
                    break
            if not placed:
                return False

        return True

    def _try_place_word(self, question: Question, existing_placement: WordPlacement) -> bool:
        """Tries to place a word connected to an existing word.

        Args:
            question: The question to place.
            existing_placement: The existing word placement to connect to.

        Returns:
            True if the word was placed successfully, False otherwise.
        """
        answer = question.answer.upper()
        existing_answer = existing_placement.question.answer.upper()

        # Finde gemeinsame Buchstaben
        for i, char in enumerate(answer):
            for j, existing_char in enumerate(existing_answer):
                if char == existing_char:
                    # Berechne mögliche Position
                    if question.orientation == Orientation.HORIZONTAL:
                        # Horizontales Wort
                        new_x = existing_placement.x + j - i
                        new_y = existing_placement.y
                    else:
                        # Vertikales Wort
                        new_x = existing_placement.x
                        new_y = existing_placement.y + j - i

                    # Prüfe ob Position gültig ist
                    if self._can_place_at(question, new_x, new_y):
                        # Platziere das Wort
                        placement = WordPlacement(
                            question=question,
                            x=new_x,
                            y=new_y,
                            length=len(answer)
                        )
                        self.placements.append(placement)

                        # Aktualisiere Gitter
                        for k, char_to_place in enumerate(answer):
                            if question.orientation == Orientation.HORIZONTAL:
                                self.grid[new_y][new_x + k] = char_to_place
                            else:
                                self.grid[new_y + k][new_x] = char_to_place

                        return True

        return False

    def _can_place_at(self, question: Question, x: int, y: int) -> bool:
        """Checks if a word can be placed at the specified position.

        Args:
            question: The question to place.
            x: The x-coordinate of the starting letter.
            y: The y-coordinate of the starting letter.

        Returns:
            True if the word can be placed at the position, False otherwise.
        """
        answer = question.answer.upper()

        # Prüfe Gittergrenzen
        if question.orientation == Orientation.HORIZONTAL:
            if x < 0 or x + len(answer) > self.width or y < 0 or y >= self.height:
                return False
        else:
            if x < 0 or x >= self.width or y < 0 or y + len(answer) > self.height:
                return False

        # Prüfe Konflikte
        for i, char in enumerate(answer):
            if question.orientation == Orientation.HORIZONTAL:
                grid_char = self.grid[y][x + i]
            else:
                grid_char = self.grid[y + i][x]

            if grid_char and grid_char != char:
                return False

        return True

    def get_problematic_questions(self) -> List[Tuple[int, str]]:
        """Identifies questions that prevent puzzle generation.

        Returns:
            A list of tuples, where each tuple contains the question number
            and an error message.
        """
        problems = []

        for i, question in enumerate(self.questions, 1):
            has_overlap = False
            for j, other_question in enumerate(self.questions, 1):
                if i != j:
                    # Prüfe ob die Antworten gemeinsame Buchstaben haben
                    if set(question.answer.upper()) & set(other_question.answer.upper()):
                        has_overlap = True
                        break

            if not has_overlap:
                problems.append((i, f"Antwort '{question.answer}' hat keine gemeinsamen Buchstaben mit anderen Antworten"))

        return problems


# LLM-FREUNDLICHE API
class LLMKreuzwortAPI:
    """Simplified API specifically for LLMs.

    Usage:
    1. Create an API instance.
    2. Add questions with add_question().
    3. Call validate_all() to find problems.
    4. Call generate() to create the puzzle.
    5. In case of errors, use get_problems().
    """

    def __init__(self, width: int = 15, height: int = 15):
        """Initializes the LLMKreuzwortAPI.

        Args:
            width: The width of the crossword grid.
            height: The height of the crossword grid.
        """
        self.riddle = KreuzwortRiddle(width, height)

    def add_question(self, question: str, answer: str, orientation: str = "horizontal") -> Dict[str, Any]:
        """Adds a question.

        Args:
            question: The question text.
            answer: The answer (must consist of letters).
            orientation: "horizontal" or "vertical".

        Returns:
            A dictionary with the status and, if applicable, error messages.
        """
        try:
            orient = Orientation.HORIZONTAL if orientation.lower() == "horizontal" else Orientation.VERTICAL
            self.riddle.add_question(question, answer, orient)
        except ValidationError as e:
            return {
                "status": "error",
                "message": e.message,
                "problematic_questions": e.problematic_questions
            }

        return {"status": "success", "message": "Frage erfolgreich hinzugefügt"}

    def validate_all(self) -> Dict[str, Any]:
        """Validates all questions and provides detailed feedback.

        Returns:
            A dictionary with the validation status and detailed error
            information if any errors are found.
        """
        errors = self.riddle.validate_all_questions()

        if errors:
            return {
                "status": "validation_errors",
                "errors": errors,
                "suggestion": "Überprüfe die Fehlermeldungen und korrigiere die entsprechenden Fragen"
            }
        else:
            return {"status": "valid", "message": "Alle Fragen sind gültig"}

    def generate(self) -> Dict[str, Any]:
        """Generates the puzzle and returns the status.

        Returns:
            A dictionary with the generation status and a success or failure
            message.
        """
        success = self.riddle.generate_grid()

        if success:
            return {"status": "success", "message": "Rätsel erfolgreich generiert"}
        else:
            return {
                "status": "generation_failed",
                "message": "Rätsel konnte nicht generiert werden",
                "suggestion": "Rufe get_problems() auf um problematische Fragen zu identifizieren"
            }

    def get_problems(self) -> Dict[str, Any]:
        """Identifies specific problems with the questions.

        Returns:
            A dictionary containing information about the problematic
            questions.
        """
        problems = self.riddle.get_problematic_questions()

        if problems:
            return {
                "status": "problems_found",
                "problems": problems,
                "suggestion": "Entferne oder ersetze die problematischen Fragen"
            }
        else:
            return {"status": "no_problems"}

    def get_grid(self) -> List[List[str]]:
        """Returns the current grid.

        Returns:
            A 2D list representing the crossword grid.
        """
        return self.riddle.grid

    def get_placements(self) -> List[Dict[str, Any]]:
        """Returns the placements of the words.

        Returns:
            A list of dictionaries, where each dictionary represents a word
            placement.
        """
        return [
            {
                "question": placement.question.question_text,
                "answer": placement.question.answer,
                "number": placement.question.number,
                "orientation": placement.question.orientation.value,
                "x": placement.x,
                "y": placement.y,
                "length": placement.length
            }
            for placement in self.riddle.placements
        ]


# BONUSWORT-ENTHÜLLUNGSMECHANISMUS
class BonusRevealSystem:
    """System for the progressive reveal of the bonus word.

    LLM-INFO: The following letters are available for the bonus word:
    - A maximum of ONE bonus word letter per word.
    - The bonus word is derived from the intersection points of the other
      words.
    """

    def __init__(self):
        """Initializes the BonusRevealSystem."""
        self.available_letters: Set[str] = set()
        self.revealed_positions: List[Tuple[int, int]] = []
        self.bonus_word: str = ""
        self.revealed_letters: List[str] = []

    def get_bonus_letter_info(self) -> Dict[str, Any]:
        """Provides the LLM with information about available letters for the
        bonus word.

        Returns:
            A dictionary with information about the available letters,
            revealed positions, bonus word length, and revealed letters.
        """
        return {
            "available_letters": list(self.available_letters),
            "revealed_positions": self.revealed_positions,
            "bonus_word_length": len(self.bonus_word) if self.bonus_word else 0,
            "revealed_letters": self.revealed_letters
        }

    def update_available_letters(self, grid: List[List[str]]) -> None:
        """Updates the available letters based on the current state of the
        grid.

        Args:
            grid: The current crossword grid.
        """
        self.available_letters.clear()

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell and (x, y) not in self.revealed_positions:
                    self.available_letters.add(cell)

    def can_reveal_bonus_letter(self) -> bool:
        """Checks if a new letter of the bonus word can be revealed.

        Returns:
            True if a new letter can be revealed, False otherwise.
        """
        return len(self.available_letters) > 0 and len(self.revealed_letters) < len(self.bonus_word)

    def reveal_next_letter(self) -> Optional[str]:
        """Reveals the next letter of the bonus word.

        Returns:
            The revealed letter, or None if no letter can be revealed.
        """
        if not self.can_reveal_bonus_letter():
            return None

        # Finde den nächsten Buchstaben im Bonuswort
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                if letter in self.available_letters:
                    if i < len(self.revealed_letters):
                        self.revealed_letters[i] = letter
                    else:
                        self.revealed_letters.append(letter)
                    return letter

        return None

    def set_bonus_word(self, word: str) -> None:
        """Sets the bonus word.

        Args:
            word: The bonus word.
        """
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)

    def get_bonus_word_hint(self) -> str:
        """Provides the LLM with a hint for the bonus word.

        Returns:
            A string with the current state of the bonus word.
        """
        if not self.bonus_word:
            return "Kein Bonuswort gesetzt"

        revealed = ''.join(self.revealed_letters)
        return f"Bonuswort: {revealed} ({len(self.revealed_letters)}/{len(self.bonus_word)} Buchstaben)"


# BEISPIEL-NUTZUNG FÜR LLMs
if __name__ == "__main__":
    """
    Example for LLMs with bonus word information.
    """
    # Beispiel für die grundlegende Nutzung
    api = LLMKreuzwortAPI()
    
    # Beispielfragen hinzufügen
    api.add_question("Hauptstadt von Deutschland", "Berlin", "horizontal")
    api.add_question("Hauptstadt von Frankreich", "Paris", "vertical")
    
    # Validieren
    validation = api.validate_all()
    print(f"Validierung: {validation}")
    
    # Generieren
    generation = api.generate()
    print(f"Generierung: {generation}")
    
    # Bonuswort-System
    bonus_system = BonusRevealSystem()
    bonus_system.set_bonus_word("EUROPA")
    
    if generation["status"] == "success":
        bonus_system.update_available_letters(api.get_grid())
        print(f"Bonuswort-Info: {bonus_system.get_bonus_letter_info()}")
