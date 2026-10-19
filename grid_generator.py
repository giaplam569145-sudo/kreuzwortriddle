from typing import List

from models import Orientation, Question, WordPlacement


class GridGenerator:
    """Handles the generation of the crossword grid."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid: List[List[str]] = [['' for _ in range(width)] for _ in range(height)]
        self.placements: List[WordPlacement] = []

    def generate(self, questions: List[Question]) -> bool:
        """Generates the grid with the given questions.

        Args:
            questions: List of questions to place.

        Returns:
            True if successful, False otherwise.
        """
        self.placements.clear()
        self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]

        # Sort questions by length to improve placement efficiency
        sorted_questions = sorted(questions, key=lambda q: len(q.answer), reverse=True)

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
                if question.orientation == Orientation.HORIZONTAL:
                    y, x = placement_to_remove.y, placement_to_remove.x + i
                else:
                    y, x = placement_to_remove.y + i, placement_to_remove.x

                # Check if this cell is part of another word
                is_part_of_other_word = False
                for p in self.placements:
                    if p.question.orientation == Orientation.HORIZONTAL:
                        if p.y == y and p.x <= x < p.x + p.length:
                            is_part_of_other_word = True
                            break
                    else: # Vertical
                        if p.x == x and p.y <= y < p.y + p.length:
                            is_part_of_other_word = True
                            break

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
