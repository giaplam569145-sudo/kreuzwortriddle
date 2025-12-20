#!/usr/bin/env python3
"""Crossword Riddle Framework for LLMs.

A Python framework for the automatic creation of crossword puzzles.
Written for LLMs - focuses on questions/answers, not on logic.

Author: Qwen Code (2025)
"""

from typing import Dict, List, Tuple, Optional, Any
from gamemode import GameMode
from models import Question, Orientation, WordPlacement, ValidationError
from bonus_system import BonusSystem
from grid_generator import GridGenerator


class KreuzwortRiddle:
    """Main class for creating the crossword puzzle.

    Attributes:
        width: The width of the crossword grid.
        height: The height of the crossword grid.
        questions: A list of Question objects.
        grid_generator: The generator for the grid.
        bonus_system: The system for managing bonus words.
    """

    def __init__(self, width: int = 15, height: int = 15, game_mode: Optional[GameMode] = None):
        """Initializes the KreuzwortRiddle.

        Args:
            width: The width of the crossword grid.
            height: The height of the crossword grid.
            game_mode: The game mode to use.
        """
        self.width = width
        self.height = height
        self.questions: List[Question] = []
        self.game_mode = game_mode
        self.grid_generator = GridGenerator(width, height)
        self.bonus_system = BonusSystem()

    @property
    def grid(self) -> List[List[str]]:
        """Returns the current grid from the generator."""
        return self.grid_generator.grid

    @property
    def placements(self) -> List[WordPlacement]:
        """Returns the current placements from the generator."""
        return self.grid_generator.placements

    @property
    def bonus_word(self) -> str:
        return self.bonus_system.bonus_word

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
        """Tries to generate the crossword puzzle grid using the generator.

        Returns:
            True if the grid was generated successfully, False otherwise.
        """
        if self.game_mode:
            self.game_mode.apply(self)

        if not self.questions:
            return False

        # Reset generator dimensions in case they were changed (though not exposed in init currently)
        self.grid_generator.width = self.width
        self.grid_generator.height = self.height

        return self.grid_generator.generate(self.questions)

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

    # Delegate to BonusSystem
    def set_bonus_word(self, word: str) -> None:
        self.bonus_system.set_bonus_word(word)

    def reveal_next_letter(self) -> Optional[str]:
        return self.bonus_system.reveal_next_letter(self.grid)

    def get_bonus_word_hint(self) -> str:
        return self.bonus_system.get_bonus_word_hint()


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
