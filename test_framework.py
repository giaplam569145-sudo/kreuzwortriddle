#!/usr/bin/env python3
"""
Pytest-Tests fuer das Kreuzwort-Riddle Framework
"""

import pytest

from kreuzwortriddle import (
    BonusRevealSystem,
    BonusWordConstraints,
    KreuzwortRiddle,
    LLMKreuzwortAPI,
    ValidationError,
)

# ── Fixtures ──────────────────────────────────────────────────────────

@pytest.fixture
def api():
    return LLMKreuzwortAPI()


@pytest.fixture
def api_with_words():
    a = LLMKreuzwortAPI(width=15, height=15)
    a.add_question("Hauptstadt von Deutschland", "Berlin", "horizontal")
    a.add_question("Fluss in Deutschland", "Elbe", "vertical")
    a.add_question("Bundesland", "Bayern", "horizontal")
    a.add_question("Gebirge", "Alpen", "vertical")
    return a


    def test_get_problematic_questions(self):
        """Test identifying problematic questions."""
        self.api.add_question("No overlap", "abc", "horizontal")
        self.api.add_question("Different letters", "def", "vertical")
        result = self.api.get_problems()
        self.assertEqual(result["status"], "problems_found")
        self.assertIn("has no common letters", result["problems"][0][1])

@pytest.fixture
def bonus():
    return BonusRevealSystem()


@pytest.fixture
def bonus_with_grid():
    b = BonusRevealSystem()
    b.set_bonus_word("EUROPA")
    sim_grid = [
        ['', 'E', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['U', '', 'R', '', '', ''],
        ['', '', '', '', 'O', ''],
        ['', 'P', '', 'A', '', ''],
        ['', '', '', '', '', ''],
    ]
    b.update_available_letters(sim_grid)
    return b


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

@pytest.fixture
def constraints():
    return BonusWordConstraints()


# ── Validierung ───────────────────────────────────────────────────────

class TestValidierung:
    def test_gueltige_frage(self, api):
        result = api.add_question("Hauptstadt", "Berlin", "horizontal")
        assert result["status"] == "success"

    def test_leere_frage(self, api):
        result = api.add_question("", "Test", "horizontal")
        assert result["status"] == "error"

    def test_vertikale_frage(self, api):
        result = api.add_question("Stadt", "Paris", "vertical")
        assert result["status"] == "success"

    def test_validate_all_ok(self, api):
        api.add_question("Frage1", "Berlin", "horizontal")
        api.add_question("Frage2", "Paris", "vertical")
        assert api.validate_all()["status"] == "valid"

    def test_keine_probleme(self, api):
        api.add_question("Frage1", "Berlin", "horizontal")
        api.add_question("Frage2", "Paris", "vertical")
        assert api.get_problems()["status"] == "no_problems"

    def test_antwort_mit_zahlen(self, api):
        result = api.add_question("Frage", "Test123", "horizontal")
        assert result["status"] == "error"

    def test_zu_kurz(self, api):
        result = api.add_question("Frage", "A", "horizontal")
        assert result["status"] == "error"

    def test_zu_lang(self, api):
        result = api.add_question("Frage", "A" * 21, "horizontal")
        assert result["status"] == "error"

    def test_validation_error_raised(self):
        r = KreuzwortRiddle()
        with pytest.raises(ValidationError):
            r.add_question("", "Test")


# ── Gitter-Generierung ───────────────────────────────────────────────

class TestGitterGenerierung:
    def test_vier_woerter(self, api_with_words):
        result = api_with_words.generate()
        assert result["status"] == "success"

    def test_alle_platziert(self, api_with_words):
        api_with_words.generate()
        assert len(api_with_words.get_placements()) == 4

    def test_zwei_woerter(self):
        a = LLMKreuzwortAPI()
        a.add_question("Stadt", "Berlin", "horizontal")
        a.add_question("Fluss", "Elbe", "vertical")
        assert a.generate()["status"] == "success"

    def test_keine_fragen(self):
        a = LLMKreuzwortAPI()
        assert a.generate()["status"] == "generation_failed"

    def test_kein_erreichtes_wort(self):
        a = LLMKreuzwortAPI()
        a.add_question("Frage1", "Berlin", "horizontal")
        a.add_question("Frage2", "Tokyo", "vertical")
        a.add_question("Frage3", "Quiz", "horizontal")
        assert a.generate()["status"] == "generation_failed"

    def test_gitter_nicht_leer(self, api_with_words):
        api_with_words.generate()
        grid = api_with_words.get_grid()
        non_empty = sum(1 for row in grid for cell in row if cell)
        assert non_empty > 0

    def test_platzierungen_kreuzen(self, api_with_words):
        api_with_words.generate()
        placements = api_with_words.get_placements()
        horiz = [p for p in placements if p["orientation"] == "horizontal"]
        vert = [p for p in placements if p["orientation"] == "vertical"]
        assert len(horiz) >= 1
        assert len(vert) >= 1

    def test_fuenf_woerter(self):
        a = LLMKreuzwortAPI()
        for q, a_, o in [
            ("F1", "ABCDE", "horizontal"),
            ("F2", "BCDEF", "vertical"),
            ("F3", "CDEFG", "horizontal"),
            ("F4", "DEFGH", "vertical"),
            ("F5", "EFGHI", "horizontal"),
        ]:
            a.add_question(q, a_, o)
        assert a.generate()["status"] == "success"

    def test_vertikales_erstes_wort(self):
        a = LLMKreuzwortAPI()
        a.add_question("F1", "BERLIN", "vertical")
        a.add_question("F2", "ELBE", "horizontal")
        assert a.generate()["status"] == "success"


# ── Problematische Fragen ────────────────────────────────────────────

class TestProbleme:
    def test_problem_erkannt(self):
        a = LLMKreuzwortAPI()
        a.add_question("Frage", "Berlin", "horizontal")
        a.add_question("Frage2", "Wado", "vertical")
        problems = a.get_problems()
        assert problems["status"] == "problems_found"

    def test_geometrisches_problem(self):
        a = LLMKreuzwortAPI(width=5, height=5)
        a.add_question("F1", "ABCDE", "horizontal")
        a.add_question("F2", "BCD", "vertical")
        problems = a.get_problems()
        assert problems["status"] == "no_problems"

    def test_zu_lang_fuer_gitter(self):
        a = LLMKreuzwortAPI(width=5, height=5)
        a.add_question("F1", "ABCDEF", "horizontal")
        a.add_question("F2", "XYZ", "vertical")
        problems = a.get_problems()
        assert problems["status"] == "problems_found"
        msg = problems["problems"][0][1]
        assert "zu lang" in msg.lower()

    def test_gleiche_orientierung_alle(self):
        a = LLMKreuzwortAPI()
        a.add_question("F1", "HALLO", "horizontal")
        a.add_question("F2", "WELT", "horizontal")
        a.add_question("F3", "TEST", "horizontal")
        p = a.get_problems()
        assert p["status"] == "problems_found"
        assert len(p["problems"]) == 3


# ── Bonuswort-System ─────────────────────────────────────────────────

class TestBonusSystem:
    def test_set_bonus_word(self, bonus):
        bonus.set_bonus_word("EUROPA")
        assert bonus.bonus_word == "EUROPA"

    def test_hint_zeigt_unterstriche(self, bonus):
        bonus.set_bonus_word("EUROPA")
        assert "_" in bonus.get_bonus_word_hint()

    def test_hint_zeigt_vollstaendig(self, bonus):
        bonus.set_bonus_word("AA")
        grid = [['A', 'A'], ['', '']]
        bonus.update_available_letters(grid)
        bonus.reveal_next_letter()
        bonus.reveal_next_letter()
        assert "VOLLSTAENDIG" in bonus.get_bonus_word_hint()

    def test_is_complete_false(self, bonus):
        bonus.set_bonus_word("ABC")
        assert bonus.is_complete is False

    def test_is_complete_true(self, bonus):
        bonus.set_bonus_word("A")
        grid = [['A']]
        bonus.update_available_letters(grid)
        bonus.reveal_next_letter()
        assert bonus.is_complete is True

    def test_is_complete_ohne_bonus(self, bonus):
        assert bonus.is_complete is False

    def test_get_info_enthält_is_complete(self, bonus):
        bonus.set_bonus_word("X")
        info = bonus.get_bonus_letter_info()
        assert "is_complete" in info

    def test_available_letters(self, bonus_with_grid):
        assert len(bonus_with_grid.available_letters) > 0

    def test_can_reveal(self, bonus_with_grid):
        assert bonus_with_grid.can_reveal_bonus_letter() is True

    def test_reveal_erster_buchstabe(self, bonus_with_grid):
        letter = bonus_with_grid.reveal_next_letter()
        assert letter is not None

    def test_revealed_positions_befuellt(self, bonus_with_grid):
        bonus_with_grid.reveal_next_letter()
        assert len(bonus_with_grid.revealed_positions) > 0

    def test_reveal_mehrere_buchstaben(self, bonus_with_grid):
        letters = []
        for _ in range(3):
            letter = bonus_with_grid.reveal_next_letter()
            if letter:
                letters.append(letter)
        assert len(letters) == 3

    def test_reveal_ohne_available(self):
        b = BonusRevealSystem()
        b.set_bonus_word("TEST")
        assert b.can_reveal_bonus_letter() is False

    def test_reveal_ohne_bonus(self):
        b = BonusRevealSystem()
        b.available_letters = {'A'}
        assert b.can_reveal_bonus_letter() is False

    def test_duplikat_buchstaben_effect(self):
        b = BonusRevealSystem()
        b.set_bonus_word("EFFECT")
        grid = [['E', 'F', 'F', 'E', 'C', 'T'], ['', '', '', '', '', '']]
        b.update_available_letters(grid)
        revealed = 0
        for _ in range(6):
            if b.reveal_next_letter():
                revealed += 1
        assert revealed == 6
        assert b.is_complete is True

    def test_duplikat_buchstaben_banana(self):
        b = BonusRevealSystem()
        b.set_bonus_word("BANANA")
        grid = [['B', 'A', 'N', 'A', 'N', 'A'], ['', '', '', '', '', '']]
        b.update_available_letters(grid)
        for _ in range(6):
            b.reveal_next_letter()
        assert b.is_complete is True


# ── BonusWordConstraints ─────────────────────────────────────────────

class TestConstraints:
    def test_defaults(self, constraints):
        assert constraints.max_bonus_length == 8
        assert constraints.min_bonus_length == 3

    def test_calculate_max(self, constraints):
        assert constraints.calculate_max_bonus_length(5) == 5
        assert constraints.calculate_max_bonus_length(2) == 3

    def test_gueltiges_bonuswort(self, constraints):
        errors = constraints.validate_bonus_word("EUROPA", {'E', 'U', 'R', 'O', 'P', 'A'})
        assert len(errors) == 0

    def test_ungueltiges_bonuswort(self, constraints):
        errors = constraints.validate_bonus_word("XYZ", {'E', 'U', 'R'})
        assert len(errors) > 0

    def test_leeres_bonuswort(self, constraints):
        errors = constraints.validate_bonus_word("", set())
        assert len(errors) > 0

    def test_zu_kurzes_bonuswort(self, constraints):
        errors = constraints.validate_bonus_word("AB", {'A', 'B'})
        assert len(errors) > 0

