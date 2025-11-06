#!/usr/bin/env python3
"""
Kreuzwort-Riddle Framework für LLMs
Ein Python-Framework zur automatischen Erstellung von Kreuzworträtseln

Für LLMs geschrieben - konzentriert sich auf Fragen/Antworten, nicht auf Logik
Autor: Qwen Code (2025)
"""

import json
from typing import Dict, List, Tuple, Optional, Set, Any
from dataclasses import dataclass, field
from enum import Enum
import random


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
    
    def overlaps_with(self, other: 'WordPlacement') -> bool:
        """Prüft ob sich zwei Wörter überschneiden"""
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
        """Versucht das Rätsel zu generieren - gibt True bei Erfolg zurück"""
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
        """Versucht ein Wort an bestehendes Wort anzuschließen"""
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
                        for k, char in enumerate(answer):
                            if question.orientation == Orientation.HORIZONTAL:
                                self.grid[new_y][new_x + k] = char
                            else:
                                self.grid[new_y + k][new_x] = char
                        
                        return True
        
        return False
        
    def _can_place_at(self, question: Question, x: int, y: int) -> bool:
        """Prüft ob ein Wort an der angegebenen Position platziert werden kann"""
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
        
    def get_bonus_letter_info(self) -> Dict[str, Any]:
        """
        Gibt dem LLM Informationen über verfügbare Buchstaben für das Bonuswort.
        """
        return {
            "available_letters": list(self.available_letters),
            "revealed_positions": self.revealed_positions,
            "bonus_word_length": len(self.bonus_word) if self.bonus_word else 0,
            "revealed_letters": self.revealed_letters
        }
        
    def update_available_letters(self, grid: List[List[str]]) -> None:
        """
        Aktualisiert die verfügbaren Buchstaben basierend auf dem aktuellen Gitterzustand.
        """
        self.available_letters.clear()
        
        for y, row in enumerate(grid):
            for x, cell in enumerate(row):
                if cell and (x, y) not in self.revealed_positions:
                    self.available_letters.add(cell)
        
    def can_reveal_bonus_letter(self) -> bool:
        """
        Prüft ob ein neuer Buchstabe des Bonuswortes aufgedeckt werden kann.
        """
        return len(self.available_letters) > 0 and len(self.revealed_letters) < len(self.bonus_word)
        
    def reveal_next_letter(self) -> Optional[str]:
        """
        Deckt den nächsten Buchstaben des Bonuswortes auf.
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
        """
        Setzt das Bonuswort.
        """
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)
        
    def get_bonus_word_hint(self) -> str:
        """
        Gibt dem LLM einen Hinweis für das Bonuswort.
        """
        if not self.bonus_word:
            return "Kein Bonuswort gesetzt"
            
        revealed = ''.join(self.revealed_letters)
        return f"Bonuswort: {revealed} ({len(self.revealed_letters)}/{len(self.bonus_word)} Buchstaben)"


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