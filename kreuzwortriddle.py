#!/usr/bin/env python3
"""
Kreuzwort-Riddle Framework für LLMs
Ein Python-Framework zur automatischen Erstellung von Kreuzworträtseln

Für LLMs geschrieben - konzentriert sich auf Fragen/Antworten, nicht auf Logik
Autor: Qwen Code (2025)
"""

from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
from itertools import permutations


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
    def __init__(self, message: str, problematic_questions: List[Tuple[int, str]] = None):
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
        """Fügt eine Frage hinzu mit automatischer Validierung"""
        new_question = Question(question, answer, len(self.questions) + 1, orientation)
        errors = new_question.validate()
        
        if errors:
            raise ValidationError(
                f"Frage {len(self.questions) + 1} ist ungültig: {', '.join(errors)}",
                [(len(self.questions) + 1, error) for error in errors]
            )
        
        self.questions.append(new_question)
        
    def validate_all_questions(self) -> List[str]:
        """Validiert alle Fragen und gibt eine Liste von Fehlern zurück"""
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

        if len(self.questions) <= 8:
            for perm in permutations(self.questions[1:]):
                ordered = [self.questions[0]] + list(perm)
                self.placements.clear()
                self.grid = [['' for _ in range(self.width)] for _ in range(self.height)]
                if self._try_generate(ordered):
                    return True

        return False

    def _try_generate(self, questions: List[Question]) -> bool:
        """Backtracking-Platzierung einer geordneten Fragenliste"""
        if not questions:
            return True

        first = questions[0]
        start_x = max(0, (self.width - len(first.answer)) // 2)
        start_y = self.height // 2

        if not self._place_word(first, start_x, start_y):
            return False

        return self._place_remaining(questions[1:], 0)

    def _place_remaining(self, remaining: List[Question], idx: int) -> bool:
        """Platziert die restlichen Wörter per Backtracking"""
        if idx >= len(remaining):
            return True

        question = remaining[idx]

        for existing in list(self.placements):
            pos = self._find_placement(question, existing)
            if pos is not None:
                px, py = pos
                saved_grid = [row[:] for row in self.grid]
                saved_placements = list(self.placements)

                self._place_word(question, px, py)

                if self._place_remaining(remaining, idx + 1):
                    return True

                self.grid = saved_grid
                self.placements = saved_placements

        return False

    def _find_placement(self, question: Question,
                        existing: WordPlacement) -> Optional[Tuple[int, int]]:
        """Sucht eine gültige Position für question an existing, gibt (x,y) oder None"""
        answer = question.answer.upper()
        existing_answer = existing.question.answer.upper()
        existing_horiz = existing.question.orientation == Orientation.HORIZONTAL

        for i, char in enumerate(answer):
            for j, ex_char in enumerate(existing_answer):
                if char == ex_char:
                    if existing_horiz:
                        cross_x = existing.x + j
                        cross_y = existing.y
                    else:
                        cross_x = existing.x
                        cross_y = existing.y + j

                    if question.orientation == Orientation.HORIZONTAL:
                        nx = cross_x - i
                        ny = cross_y
                    else:
                        nx = cross_x
                        ny = cross_y - i

                    if self._can_place_at(question, nx, ny):
                        return (nx, ny)
        return None

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
        
    def get_problematic_questions(self) -> List[Tuple[int, str]]:
        """Identifiziert Fragen, die eine Rätselerstellung verhindern"""
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
            Dict mit Status und ggf. Fehlermeldungen
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
        """Validiert alle Fragen und gibt detailliertes Feedback"""
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
        """Generiert das Rätsel und gibt Status zurück"""
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
        """Identifiziert spezifische Probleme mit den Fragen"""
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
        """Gibt das aktuelle Gitter zurück"""
        return self.riddle.grid
    
    def get_placements(self) -> List[Dict[str, Any]]:
        """Gibt die Platzierungen der Wörter zurück"""
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
        self.available_letters: Set[str] = set()
        self.revealed_positions: List[Tuple[int, int]] = []
        self.bonus_word: str = ""
        self.revealed_letters: List[str] = []
        self._grid_positions: Dict[str, List[Tuple[int, int]]] = {}
        
    def get_bonus_letter_info(self) -> Dict[str, Any]:
        """Gibt dem LLM Informationen über verfügbare Buchstaben für das Bonuswort."""
        return {
            "available_letters": list(self.available_letters),
            "revealed_positions": self.revealed_positions,
            "bonus_word_length": len(self.bonus_word) if self.bonus_word else 0,
            "revealed_letters": self.revealed_letters
        }
        
    def update_available_letters(self, grid: List[List[str]]) -> None:
        """Aktualisiert die verfügbaren Buchstaben basierend auf dem aktuellen Gitterzustand."""
        self.available_letters.clear()
        self._grid_positions.clear()
        
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell and (x, y) not in self.revealed_positions:
                    self.available_letters.add(cell)
                    self._grid_positions.setdefault(cell, []).append((x, y))
        
    def can_reveal_bonus_letter(self) -> bool:
        """Prüft ob ein neuer Buchstabe des Bonuswortes aufgedeckt werden kann."""
        if not self.available_letters or not self.bonus_word:
            return False
        return '_' in self.revealed_letters
        
    def reveal_next_letter(self) -> Optional[str]:
        """Deckt den nächsten Buchstaben des Bonuswortes auf."""
        if not self.can_reveal_bonus_letter():
            return None
            
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                if letter in self.available_letters:
                    if i < len(self.revealed_letters):
                        self.revealed_letters[i] = letter
                    else:
                        self.revealed_letters.append(letter)
                    pos = self._grid_positions.get(letter, [None])[0]
                    if pos:
                        self.revealed_positions.append(pos)
                        self.available_letters.discard(letter)
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
        return f"Bonuswort: {revealed} ({len(self.revealed_letters)}/{len(self.bonus_word)} Buchstaben)"


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