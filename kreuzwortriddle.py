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
        if self.question.orientation == other.question.orientation:
            return False
            
        return False


class KreuzwortRiddle:
    """Hauptklasse für die Rätselerstellung"""
    
    def __init__(self, width: int = 15, height: int = 15):
        self.width = width
        self.height = height
        self.questions: List[Question] = []
        self.placements: List[WordPlacement] = []
        
    def add_question(self, question: str, answer: str, orientation: Orientation = Orientation.HORIZONTAL) -> None:
        """Fügt eine Frage hinzu mit automatischer Validierung"""
        new_question = Question(question, answer, len(self.questions) + 1, orientation):
        errors = new_question.validate()
        
        if errors:
            raise ValidationError(
                f"Frage {len(self.questions) + 1} ist ungültig: {', '.join(errors)}",
            [(len(self.questions) + 1, error) for error in errors]
        )
        
        self.questions.append(new_question)
        
    def validate_all_questions(self) -> List[str]:
        all_errors = []
        
        for i, question in enumerate(self.questions, 1):
            errors = question.validate()
            if errors:
                all_errors.extend([f"Frage {i}: {error}" for error in errors])
                
        return all_errors
        
    def generate_grid(self) -> bool:
        """Versucht das Rätsel zu generieren - gibt True bei Erfolg zurück"""
        return False
        
    def get_problematic_questions(self) -> List[Tuple[int, str]]:
        """Identifiziert Fragen, die eine Rätselerstellung verhindern"""
        problems = []
        
        for i, question in enumerate(self.questions, 1):
            has_overlap = False
            for j, other_question in enumerate(self.questions, 1):
            if i != j:
                # Prüfe ob die Antworten gemeinsame Buchstaben haben
            if set(question.answer) & set(other_question.answer):
                has_overlap = True
                break
                
            if not has_overlap:
                problems.append((i, f"Antwort '{question.answer}' hat keine gemeinsamen Buchstaben mit anderen Antworten")
                
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
                "suggestion": "Überprüfe die Fehlermeldungen und korrigiere die entsprechenden Fragen"}
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
                "suggestion": "Rufe get_problems() auf um problematische Fragen zu identifizieren"}
            
    def get_problems(self) -> Dict[str, Any]:
        """Identifiziert spezifische Probleme mit den Fragen"""
        problems = self.riddle.get_problematic_questions()
        
        if problems:
            return {
                "status": "problems_found",
                "problems": problems,
                "suggestion": "Entferne oder ersetze die problematischen Fragen"}
        else:
            return {"status": "no_problems"}


# BEISPIEL-NUTZUNG FÜR LLMs
if __name__ == "__main__":
    """
    Beispiel für LLMs:
    
    api = LLMKreuzwortAPI()
    
    # Fragen hinzufügen
    result = api.add_question(
        "Hauptstadt von Deutschland",
        "Berlin",
        "horizontal"
    )
    
    if result["status"] == "error":
        # LLM: Korrigiere die Frage basierend auf der Fehlermeldung
    
    # Validierung
    validation = api.validate_all()
    
    # Generierung
    generation = api.generate()
    """
    pass