#!/usr/bin/env python3
"""Crossword Riddle Framework for LLMs.

A Python framework for the automatic creation of crossword puzzles.
Written for LLMs - focuses on questions/answers, not on logic.

Author: Qwen Code (2025)
"""

import json
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import random
from gamemode import GameMode


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
    allow_numbers: bool = False

    def validate(self) -> List[str]:
        """Validates the question and returns a list of errors.

        Returns:
            A list of strings, where each string is an error message.
        """
        errors = []

        if not self.question_text.strip():
            errors.append("Question text is empty")
        if not self.answer.strip():
            errors.append("Answer is empty")
        if len(self.answer) < 2:
            errors.append("Answer must be at least 2 letters long")
        if not self.allow_numbers and not self.answer.isalpha():
            errors.append("Answer must only contain letters")
        if self.allow_numbers and not self.answer.isalnum():
            errors.append("Answer must only contain letters and numbers")
        if len(self.answer) > 20:
            errors.append("Answer is too long (max 20 letters)")

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

        # Check if the words intersect
        if self.question.orientation == Orientation.HORIZONTAL:
            # Horizontal word intersects vertical word
            return (self.x <= other.x < self.x + self.length and
                    other.y <= self.y < other.y + other.length)
        else:
            # Vertical word intersects horizontal word
            return (other.x <= self.x < other.x + other.length and
                    self.y <= other.y < self.y + other.length)


class KreuzwortRiddle:
    """Main class for creating the crossword puzzle.

    Attributes:
        width: The width of the crossword grid.
        height: The height of the crossword grid.
        questions: A list of Question objects.
        placements: A list of WordPlacement objects.
        grid: A 2D list representing the crossword grid.
    """

    def __init__(self, width: int = 15, height: int = 15, game_mode: Optional[GameMode] = None):
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
        self.game_mode = game_mode
        self.bonus_word: str = ""
        self.revealed_letters: List[str] = []

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

        if self.game_mode:
            self.game_mode.new_question_created(new_question)

        errors = new_question.validate()

        if errors:
            raise ValidationError(
                f"Question {len(self.questions) + 1} is invalid: {', '.join(errors)}",
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
                all_errors.extend([f"Question {i}: {error}" for error in errors])

        return all_errors

    def generate_grid(self) -> bool:
        """Tries to generate the crossword puzzle grid using a backtracking algorithm.

        Returns:
            True if the grid was generated successfully, False otherwise.
        """
        if self.game_mode:
            self.game_mode.apply(self)

        if not self.questions:
            return False

        self.placements.clear()
        self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]

        # Sort questions by length to improve placement efficiency
        sorted_questions = sorted(self.questions, key=lambda q: len(q.answer), reverse=True)

        return self._backtrack_generate(sorted_questions)

    def _backtrack_generate(self, questions_to_place: List[Question]) -> bool:
        """Recursively tries to place words on the grid.

        Args:
            questions_to_place: A list of Question objects to be placed on the grid.

        Returns:
            True if all questions were placed successfully, False otherwise.
        """
        if not questions_to_place:
            return True  # All questions have been placed

        question = questions_to_place[0]

        for y in range(self.height):
            for x in range(self.width):
                if self._can_place_at(question, x, y):
                    self._place_word(question, x, y)
                    if self._backtrack_generate(questions_to_place[1:]):
                        return True
                    self._remove_word(question)  # Backtrack

        return False

    def _place_word(self, question: Question, x: int, y: int) -> None:
        """Places a word on the grid at the specified position.

        Args:
            question: The question to place.
            x: The x-coordinate of the starting letter.
            y: The y-coordinate of the starting letter.
        """
        answer = question.answer.upper()
        placement = WordPlacement(question=question, x=x, y=y, length=len(answer))
        self.placements.append(placement)

        for i, char in enumerate(answer):
            if question.orientation == Orientation.HORIZONTAL:
                self.grid[y][x + i] = char
            else:
                self.grid[y + i][x] = char

    def _remove_word(self, question: Question) -> None:
        """Removes a word from the grid, handling intersections correctly."""
        placement_to_remove = next((p for p in self.placements if p.question == question), None)

        if placement_to_remove:
            self.placements.remove(placement_to_remove)
            answer = question.answer.upper()

            for i, _ in enumerate(answer):
                y, x = (placement_to_remove.y, placement_to_remove.x + i) if question.orientation == Orientation.HORIZONTAL else (placement_to_remove.y + i, placement_to_remove.x)

                is_part_of_other_word = any(
                    (p.y <= y < p.y + p.length and p.x == x) if p.question.orientation == Orientation.VERTICAL else (p.x <= x < p.x + p.length and p.y == y)
                    for p in self.placements
                )

                if not is_part_of_other_word:
                    self.grid[y][x] = ''

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

        if question.orientation == Orientation.HORIZONTAL:
            if x + len(answer) > self.width:
                return False
        else:
            if y + len(answer) > self.height:
                return False

        for i, char in enumerate(answer):
            grid_char = self.grid[y][x + i] if question.orientation == Orientation.HORIZONTAL else self.grid[y + i][x]

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
                    if set(question.answer.upper()) & set(other_question.answer.upper()):
                        has_overlap = True
                        break

            if not has_overlap:
                problems.append((i, f"Answer '{question.answer}' has no common letters with other answers"))

        return problems

    def set_bonus_word(self, word: str) -> None:
        """Sets the bonus word.

        Args:
            word: The bonus word.
        """
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)

    def reveal_next_letter(self) -> Optional[str]:
        """Reveals the next letter of the bonus word.

        Returns:
            The revealed letter, or None if no letter can be revealed.
        """
        if not self.can_reveal_bonus_letter():
            return None

        available_letters = self.get_available_letters()
        for i, letter in enumerate(self.bonus_word):
            if self.revealed_letters[i] == '_' and letter in available_letters:
                self.revealed_letters[i] = letter
                return letter

        return None

    def can_reveal_bonus_letter(self) -> bool:
        """Checks if a new letter of the bonus word can be revealed.

        Returns:
            True if a new letter can be revealed, False otherwise.
        """
        return '_' in self.revealed_letters and any(
            letter in self.get_available_letters() for letter in self.bonus_word
        )

    def get_available_letters(self) -> Set[str]:
        """Gets the set of available letters from the grid.

        Returns:
            A set of strings, where each string is an available letter.
        """
        available = set()
        for row in self.grid:
            for cell in row:
                if cell:
                    available.add(cell)
        return available

    def get_bonus_word_hint(self) -> str:
        """Provides the LLM with a hint for the bonus word.

        Returns:
            A string with the current state of the bonus word.
        """
        if not self.bonus_word:
            return "No bonus word set"

        return f"Bonus word: {''.join(self.revealed_letters)}"


# LLM-FRIENDLY API
class LLMKreuzwortAPI:
    """Simplified API specifically for LLMs.

    Usage:
    1. Create an API instance.
    2. Add questions with add_question().
    3. Call validate_all() to find problems.
    4. Call generate() to create the puzzle.
    5. In case of errors, use get_problems().
    """

    def __init__(self, width: int = 15, height: int = 15, game_mode: Optional[GameMode] = None):
        """Initializes the LLMKreuzwortAPI.

        Args:
            width: The width of the crossword grid.
            height: The height of the crossword grid.
        """
        self.riddle = KreuzwortRiddle(width, height, game_mode)

    def set_game_mode(self, game_mode: GameMode):
        """Sets the game mode for the riddle.

        Args:
            game_mode: The game mode to set.
        """
        self.riddle.game_mode = game_mode

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

        return {"status": "success", "message": "Question added successfully"}

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
                "suggestion": "Review the error messages and correct the corresponding questions"
            }
        else:
            return {"status": "valid", "message": "All questions are valid"}

    def generate(self) -> Dict[str, Any]:
        """Generates the puzzle and returns the status.

        Returns:
            A dictionary with the generation status and a success or failure
            message.
        """
        success = self.riddle.generate_grid()

        if success:
            return {"status": "success", "message": "Riddle generated successfully"}
        else:
            return {
                "status": "generation_failed",
                "message": "Could not generate riddle",
                "suggestion": "Call get_problems() to identify problematic questions"
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
                "suggestion": "Remove or replace the problematic questions"
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

    def set_bonus_word(self, word: str) -> None:
        """Sets the bonus word.

        Args:
            word: The bonus word.
        """
        self.riddle.set_bonus_word(word)

    def reveal_next_bonus_letter(self) -> Optional[str]:
        """Reveals the next letter of the bonus word.

        Returns:
            The revealed letter, or None if no letter can be revealed.
        """
        return self.riddle.reveal_next_letter()

    def get_bonus_word_hint(self) -> str:
        """Provides a hint for the bonus word.

        Returns:
            A string with the current state of the bonus word.
        """
        return self.riddle.get_bonus_word_hint()

# EXAMPLE USAGE FOR LLMs
if __name__ == "__main__":
    """
    Example for LLMs with bonus word information.
    """
    api = LLMKreuzwortAPI()
    
    api.add_question("Capital of Germany", "Berlin", "horizontal")
    api.add_question("Capital of France", "Paris", "vertical")
    
    validation = api.validate_all()
    print(f"Validation: {validation}")
    
    generation = api.generate()
    print(f"Generation: {generation}")
    
    api.set_bonus_word("EUROPA")
    
    if generation["status"] == "success":
        print(f"Bonus word hint: {api.get_bonus_word_hint()}")
        api.reveal_next_bonus_letter()
        print(f"Bonus word hint after reveal: {api.get_bonus_word_hint()}")
