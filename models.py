from enum import Enum
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

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
        allow_numbers: Whether the answer can contain numbers.
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
