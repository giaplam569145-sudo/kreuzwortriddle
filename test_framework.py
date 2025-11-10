#!/usr/bin/env python3
"""Test cases for the Kreuzwort-Riddle Framework.

These tests demonstrate the LLM-friendly API and automatic validation.
"""

import unittest
from kreuzwortriddle import LLMKreuzwortAPI, ValidationError, Question
from modes import ThemeBasedRiddle, NumberRiddle, ReverseRiddle

class TestKreuzwortRiddleAPI(unittest.TestCase):
    """Test suite for the LLMKreuzwortAPI."""

    def setUp(self):
        """Set up a new API instance for each test."""
        self.api = LLMKreuzwortAPI()

    def test_add_valid_question(self):
        """Test adding a valid question."""
        result = self.api.add_question("Capital of Germany", "Berlin", "horizontal")
        self.assertEqual(result["status"], "success")

    def test_add_invalid_question(self):
        """Test adding an invalid question."""
        result = self.api.add_question("", "Test", "horizontal")
        self.assertEqual(result["status"], "error")
        self.assertIn("Question text is empty", result["message"])

    def test_validate_all_with_errors(self):
        """Test validate_all with validation errors."""
        invalid_question = Question("Short answer", "A", 1)
        self.api.riddle.questions.append(invalid_question)
        result = self.api.validate_all()
        self.assertEqual(result["status"], "validation_errors")
        self.assertIn("Answer must be at least 2 letters long", result["errors"][0])


    def test_generate_grid_successfully(self):
        """Test successful grid generation."""
        self.api.add_question("Capital of Germany", "Berlin", "horizontal")
        self.api.add_question("River in Germany", "Elbe", "vertical")
        result = self.api.generate()
        self.assertEqual(result["status"], "success")

    def test_get_problematic_questions(self):
        """Test identifying problematic questions."""
        self.api.add_question("No overlap", "abc", "horizontal")
        self.api.add_question("Different letters", "def", "vertical")
        result = self.api.get_problems()
        self.assertEqual(result["status"], "problems_found")
        self.assertIn("has no common letters", result["problems"][0][1])

    def test_grid_generation_with_intersections(self):
        """Test that grid generation works with intersecting words."""
        self.api.add_question("Capital of Germany", "Berlin", "horizontal")
        self.api.add_question("Capital of Italy", "Rome", "vertical")
        result = self.api.generate()
        self.assertEqual(result["status"], "success")

class TestBonusSystem(unittest.TestCase):
    """Test suite for the BonusRevealSystem."""

    def setUp(self):
        """Set up a new API instance for each test."""
        self.api = LLMKreuzwortAPI()

    def test_set_bonus_word(self):
        """Test setting the bonus word."""
        self.api.set_bonus_word("EUROPA")
        self.assertEqual(self.api.get_bonus_word_hint(), "Bonus word: ______")

    def test_reveal_bonus_letter(self):
        """Test revealing a bonus letter."""
        self.api.add_question("Capital of Germany", "Berlin", "horizontal")
        self.api.generate()
        self.api.set_bonus_word("BERLIN")
        letter = self.api.reveal_next_bonus_letter()
        self.assertEqual(letter, "B")
        self.assertEqual(self.api.get_bonus_word_hint(), "Bonus word: B_____")

class TestGameModes(unittest.TestCase):
    """Test suite for the game modes."""

    def setUp(self):
        """Set up a new API instance for each test."""
        self.api = LLMKreuzwortAPI()

    def test_theme_based_riddle(self):
        """Test the theme-based riddle game mode."""
        self.api.set_game_mode(ThemeBasedRiddle("Capital"))
        self.api.add_question("Capital of Norway", "Oslo", "horizontal")
        self.api.add_question("A fruit", "Apple", "vertical")
        self.api.generate()
        placements = self.api.get_placements()
        self.assertEqual(len(placements), 1)
        self.assertEqual(placements[0]["answer"], "Oslo")

    def test_number_riddle(self):
        """Test the number riddle game mode."""
        self.api.set_game_mode(NumberRiddle())
        result = self.api.add_question("Year of the first moon landing", "1969", "horizontal")
        self.assertEqual(result["status"], "success")

    def test_reverse_riddle(self):
        """Test the reverse riddle game mode."""
        self.api.set_game_mode(ReverseRiddle())
        self.api.add_question("A word", "hello", "horizontal")
        self.api.generate()
        placements = self.api.get_placements()
        self.assertEqual(placements[0]["answer"], "olleh")

if __name__ == "__main__":
    unittest.main()
