#!/usr/bin/env python3
"""Crossword Riddle Framework for LLMs.

A Python framework for the automatic creation of crossword puzzles.
Written for LLMs - focuses on questions/answers, not on logic.

Author: Qwen Code (2025)
"""

from collections import Counter
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple


class Orientation(Enum):
    """Ausrichtung der Wörter im Gitter"""
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"


@dataclass
class Question:
    """Eine einzelne Kreuzwortfrage mit Validierungslogik"""
    question_text: str
    answer: str
    number: int = 0
    orientation: Orientation = Orientation.HORIZONTAL

    def validate(self) -> List[str]:
        """Validiert die Frage und gibt eine Liste von Fehlern zurück"""
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
    """Spezialisierter Fehler für Validierungsprobleme"""
    def __init__(self, message: str, problematic_questions: Optional[List[Tuple[int, str]]] = None):
        self.message = message
        self.problematic_questions = problematic_questions or []
        super().__init__(self.message)


@dataclass
class WordPlacement:
    """Position eines Wortes im Gitter"""
    question: Question
    x: int
    y: int
    length: int


class KreuzwortRiddle:
    """Hauptklasse für die Rätselerstellung"""

    def __init__(self, width: int = 15, height: int = 15):
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
                all_errors.extend([f"Frage {i}: {error}" for error in errors])


        return all_errors

    def generate_grid(self) -> bool:
        """Versucht das Rätsel zu generieren — mit Backtracking und Permutationen"""
        if not self.questions:
            return False

        self.placements.clear()
        self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]

        if self._try_generate(list(self.questions)):
            return True

        remaining = self.questions[1:]
        if len(remaining) <= 8:
            from itertools import permutations
            for perm in permutations(remaining):
                ordered = [self.questions[0]] + list(perm)
                self.placements.clear()
                self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]
                if self._try_generate(ordered):
                    return True
        else:
            import random as _random
            for _ in range(100):
                shuffled = [self.questions[0]] + _random.sample(remaining, len(remaining))
                self.placements.clear()
                self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]
                if self._try_generate(shuffled):
                    return True

        return False

    def _try_generate(self, questions: List[Question]) -> bool:
        """Backtracking-Platzierung einer geordneten Fragenliste"""
        if not questions:
            return True

        first = questions[0]
        if first.orientation == Orientation.HORIZONTAL:
            start_x = max(0, (self.width - len(first.answer)) // 2)
            start_y = self.height // 2
        else:
            start_x = self.width // 2
            start_y = max(0, (self.height - len(first.answer)) // 2)

        if not self._can_place_at(first, start_x, start_y):
            return False

        self._place_word(first, start_x, start_y)
        return self._place_remaining(questions[1:], 0)

    def _place_remaining(self, remaining: List[Question], idx: int) -> bool:
        """Platziert die restlichen Wörter per Backtracking — probiert ALLE Kreuzungspositionen."""
        if idx >= len(remaining):
            return True

        question = remaining[idx]

        for existing in list(self.placements):
            for px, py in self._find_all_placements(question, existing):
                saved_grid = [row[:] for row in self.grid]
                saved_placements = list(self.placements)

                self._place_word(question, px, py)

                if self._place_remaining(remaining, idx + 1):
                    return True

                self.grid = saved_grid
                self.placements = saved_placements

        return False

    def _find_all_placements(self, question: Question,
                             existing: WordPlacement) -> List[Tuple[int, int]]:
        """Findet ALLE gültigen Kreuzungspositionen für question an existing."""
        answer = question.answer.upper()
        existing_answer = existing.question.answer.upper()
        existing_horiz = existing.question.orientation == Orientation.HORIZONTAL

        candidates: Set[Tuple[int, int]] = set()
        for i, char in enumerate(answer):
            for j, ex_char in enumerate(existing_answer):
                if char == ex_char:
                    if existing_horiz:
                        cross_x, cross_y = existing.x + j, existing.y
                    else:
                        cross_x, cross_y = existing.x, existing.y + j

                    if question.orientation == Orientation.HORIZONTAL:
                        nx, ny = cross_x - i, cross_y
                    else:
                        nx, ny = cross_x, cross_y - i

                    candidates.add((nx, ny))

        cx, cy = self.width // 2, self.height // 2
        result = [(x, y) for x, y in candidates if self._can_place_at(question, x, y)]
        result.sort(key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        return result

    def _place_word(self, question: Question, x: int, y: int) -> bool:
        """Platziert ein Wort im Gitter an (x,y). Keine Prüfungen — nur Schreiben."""
        answer = question.answer.upper()
        placement = WordPlacement(
            question=question, x=x, y=y, length=len(answer)
        )
        self.placements.append(placement)

        for k, ch in enumerate(answer):
            if question.orientation == Orientation.HORIZONTAL:
                self.grid[y][x + k] = ch
            else:
                self.grid[y + k][x] = ch
        return True

    def _can_place_at(self, question: Question, x: int, y: int) -> bool:
        """Prüft ob ein Wort an (x,y) platziert werden kann — inkl. Parallelprüfung"""
        answer = question.answer.upper()
        is_horiz = question.orientation == Orientation.HORIZONTAL

        if is_horiz:
            if x < 0 or x + len(answer) > self.width or y < 0 or y >= self.height:
                return False
        else:
            if x < 0 or x >= self.width or y < 0 or y + len(answer) > self.height:
                return False

        before_x, before_y = (x - 1, y) if is_horiz else (x, y - 1)
        if 0 <= before_x < self.width and 0 <= before_y < self.height:
            if self.grid[before_y][before_x]:
                return False

        after_x, after_y = (x + len(answer), y) if is_horiz else (x, y + len(answer))
        if 0 <= after_x < self.width and 0 <= after_y < self.height:
            if self.grid[after_y][after_x]:
                return False

        has_crossing = False
        for i, char in enumerate(answer):
            if is_horiz:
                gx, gy = x + i, y
            else:
                gx, gy = x, y + i

            grid_char = self.grid[gy][gx]
            if grid_char:
                if grid_char != char:
                    return False
                has_crossing = True
            else:
                if is_horiz:
                    for dy in (-1, 1):
                        ny = gy + dy
                        if 0 <= ny < self.height and self.grid[ny][gx]:
                            return False
                else:
                    for dx in (-1, 1):
                        nx = gx + dx
                        if 0 <= nx < self.width and self.grid[gy][nx]:
                            return False

        if self.placements and not has_crossing:
            return False

        return True

    def _could_cross_pair(self, a: Question, b: Question) -> bool:
        """Prüft ob zwei Wörter im Gitter geometrisch kreuzen könnten (Bounds + Orientierung)."""
        if a.orientation == b.orientation:
            return False

        horiz = a if a.orientation == Orientation.HORIZONTAL else b
        vert = b if a.orientation == Orientation.HORIZONTAL else a

        h_word, h_len = horiz.answer.upper(), len(horiz.answer)
        v_word, v_len = vert.answer.upper(), len(vert.answer)

        for i, h_char in enumerate(h_word):
            for j, v_char in enumerate(v_word):
                if h_char != v_char:
                    continue

                x_min = max(0, -i)
                x_max = min(self.width - h_len, self.width - 1 - i)
                y_min = max(0, j)
                y_max = min(self.height - 1, self.height - v_len + j)

                if x_min <= x_max and y_min <= y_max:
                    return True

        return False

    def get_problematic_questions(self) -> List[Tuple[int, str]]:
        """Identifiziert Fragen, die eine Rätselerstellung verhindern.

        Prüft Buchstaben-Überschneidungen UND geometrische Machbarkeit
        innerhalb der Gittergrenzen (Länge, Orientierung, Kreuzungsposition).

        """
        problems = []

        for i, question in enumerate(self.questions, 1):
        problems = []

        for i, question in enumerate(self.questions, 1):
            answer = question.answer

            max_len = (self.width if question.orientation == Orientation.HORIZONTAL
                       else self.height)
            if len(answer) > max_len:
                problems.append((
                    i,
                    f"Antwort '{answer}' ist zu lang für das Gitter "
                    f"({max_len} Zellen in {question.orientation.value}er Richtung)"
                ))
                continue

            can_cross = False
            for j, other in enumerate(self.questions, 1):
                if i == j:
                    continue
                if not (set(answer.upper()) & set(other.answer.upper())):
                    continue
                if question.orientation == other.orientation:
                    continue
                if self._could_cross_pair(question, other):
                    can_cross = True
                    break

            if not can_cross:
                has_letter_overlap = any(
                    set(answer.upper()) & set(q.answer.upper())
                    for j, q in enumerate(self.questions, 1) if j != i
                )

                if has_letter_overlap:
                    msg = (f"Antwort '{answer}' hat gemeinsame Buchstaben, "
                           "aber die Positionen erlauben keine Kreuzung im Gitter")
                else:
                    msg = f"Antwort '{answer}' hat keine gemeinsamen Buchstaben mit anderen Antworten"

                problems.append((i, msg))


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
    Vereinfachte API speziell für LLMs

    Verwendung:
    1. API-Instanz erstellen
    2. Fragen mit add_question() hinzufügen
    3. validate_all_questions() aufrufen um Probleme zu finden
    4. generate_grid() aufrufen um das Rätsel zu erstellen
    5. Bei Fehlern: get_problematic_questions() nutzen
    """

    def __init__(self, width: int = 15, height: int = 15):
        self.riddle = KreuzwortRiddle(width, height)

    def add_question(self, question: str, answer: str, orientation: str = "horizontal") -> Dict[str, Any]:
        """
        Fügt eine Frage hinzu

        Args:
            question: Der Fragetext
            answer: Die Antwort (muss aus Buchstaben bestehen)
            orientation: "horizontal" oder "vertical"


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
                "suggestion": "Review the error messages and correct the corresponding questions"
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

# BONUSWORT-ENTHÜLLUNGSMECHANISMUS
class BonusRevealSystem:
    """
    System für die progressive Enthüllung des Bonuswortes.

    LLM-INFO: Für das Bonuswort stehen folgende Buchstaben zur Verfügung:
    - Maximal EIN Bonuswortbuchstabe pro Wort
    - Das Bonuswort ergibt sich aus den Kreuzungspunkten der anderen Wörter
    """

    def __init__(self):
        self._letter_counts: Counter[str] = Counter()
        self.revealed_positions: List[Tuple[int, int]] = []
        self.bonus_word: str = ""
        self.revealed_letters: List[str] = []
        self._grid_positions: Dict[str, List[Tuple[int, int]]] = {}

    @property
    def available_letters(self) -> Set[str]:
        """Menge der noch verfügbaren Buchstaben (jeder Buchstabe max. einmal)."""
        return set(self._letter_counts.elements())

    @available_letters.setter
    def available_letters(self, letters: Set[str]) -> None:
        """Setter für Abwärtskompatibilität (jeder Buchstabe mit Count 1)."""
        self._letter_counts = Counter(letters)

    def get_bonus_letter_info(self) -> Dict[str, Any]:
        """Gibt dem LLM Informationen über verfügbare Buchstaben für das Bonuswort."""
        return {
            "available_letters": list(self.available_letters),
            "revealed_positions": self.revealed_positions,
            "bonus_word_length": len(self.bonus_word) if self.bonus_word else 0,
            "revealed_letters": self.revealed_letters,
            "is_complete": self.is_complete
        }

    def update_available_letters(self, grid: List[List[str]]) -> None:
        """Aktualisiert die verfügbaren Buchstaben basierend auf dem aktuellen Gitterzustand.

        Zählt jeden Buchstaben mit seiner tatsächlichen Häufigkeit im Gitter,
        sodass auch mehrfach vorkommende Buchstaben korrekt aufgedeckt werden können.
        """
        self._letter_counts.clear()
        self._grid_positions.clear()

        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell and (x, y) not in self.revealed_positions:
                    self._letter_counts[cell] += 1
                    self._grid_positions.setdefault(cell, []).append((x, y))

    def can_reveal_bonus_letter(self) -> bool:
        """Prüft ob ein neuer Buchstabe des Bonuswortes aufgedeckt werden kann."""
        if not self.bonus_word:
            return False
        if '_' not in self.revealed_letters:
            return False
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                if self._letter_counts.get(letter, 0) > 0:
                    return True
        return False

    def reveal_next_letter(self) -> Optional[str]:
        """Deckt den nächsten Buchstaben des Bonuswortes auf.

        Verbraucht einen Buchstaben aus dem Counter und die erste dazugehörige
        Gitterposition — dadurch werden auch Duplikat-Buchstaben korrekt abgebildet.
        """
        if not self.can_reveal_bonus_letter():
            return None

        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                count = self._letter_counts.get(letter, 0)
                if count > 0:
                    if count == 1:
                        del self._letter_counts[letter]
                    else:
                        self._letter_counts[letter] = count - 1

                    if i < len(self.revealed_letters):
                        self.revealed_letters[i] = letter
                    else:
                        self.revealed_letters.append(letter)

                    positions = self._grid_positions.get(letter)
                    if positions:
                        pos = positions.pop(0)
                        self.revealed_positions.append(pos)

                    return letter

        return None

    def set_bonus_word(self, word: str) -> None:
        """Setzt das Bonuswort."""
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)
        self.revealed_positions.clear()

    def get_bonus_word_hint(self) -> str:
        """Gibt dem LLM einen Hinweis für das Bonuswort."""
        if not self.bonus_word:
            return "Kein Bonuswort gesetzt"

        revealed = ''.join(self.revealed_letters)
        status = "VOLLSTAENDIG" if self.is_complete else "in Arbeit"
        return f"Bonuswort: {revealed} ({len(self.revealed_letters)}/{len(self.bonus_word)} Buchstaben, {status})"

    @property
    def is_complete(self) -> bool:
        """Ob das Bonuswort vollständig aufgedeckt wurde."""
        if not self.bonus_word:
            return False
        return '_' not in self.revealed_letters


class BonusWordConstraints:
    """Definiert die Einschränkungen für das Bonuswort."""

    def __init__(self):
        self.max_letters_per_word: int = 1
        self.max_bonus_length: int = 8
        self.min_bonus_length: int = 3

    def get_constraints_info(self) -> Dict[str, Any]:
        """Gibt Informationen über die Einschränkungen."""
        return {
            "max_letters_per_word": self.max_letters_per_word,
            "max_bonus_length": self.max_bonus_length,
            "min_bonus_length": self.min_bonus_length,
            "description": "Maximal ein Buchstabe pro Wort für das Bonuswort"
        }

    def calculate_max_bonus_length(self, num_questions: int) -> int:
        """Berechnet die maximale Länge des Bonuswortes basierend auf der Anzahl der Fragen."""
        calculated = min(num_questions * self.max_letters_per_word, self.max_bonus_length)
        return max(calculated, self.min_bonus_length)

    def validate_bonus_word(self, bonus_word: str, available_letters: Set[str]) -> List[str]:
        """Validiert ein Bonuswort gegen die verfügbaren Buchstaben."""
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

        word_letters = set(bonus_word.upper())
        missing_letters = word_letters - available_letters

        if missing_letters:
            errors.append(f"Fehlende Buchstaben im Gitter: {', '.join(missing_letters)}")

        return errors


# BEISPIEL-NUTZUNG FÜR LLMs
if __name__ == "__main__":
    """
    Beispiel für LLMs mit Bonuswort-Informationen.
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

