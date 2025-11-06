#!/usr/bin/env python3
"""
LLM-Informationen für Bonuswort-Enthüllung

Diese Datei enthält spezifische Informationen für LLMs:
- Welche Buchstaben für das Bonuswort verfügbar sind
- Maximal ein Bonuswortbuchstabe pro Wort möglich
- Maximale Länge des Bonuswortes basierend auf der Anzahl der Wörter
- Progressiver Enthüllungsmechanismus

Autor: Qwen Code (2025)
"""

from typing import Dict, List, Set, Tuple, Any


class LLMBonusInfo:
    """
    Spezialisierte Informationsklasse für LLMs
    
    Verwendung:
    1. LLM erhält Informationen über verfügbare Buchstaben
"""

def get_bonus_word_guidelines() -> Dict[str, Any]:
    """
    Gibt dem LLM klare Richtlinien für das Bonuswort.
    """
    
    def __init__(self):
        self.available_letters: Set[str] = set()
    self.max_bonus_length: int = 0
    
    def update_bonus_info(self, current_grid: List[List[str]]]) -> None:
        """
    Aktualisiert die Informationen über verfügbare Buchstaben für das Bonuswort.
    """
    
    def get_available_letters(self) -> Set[str]:
        """
        Gibt die aktuell verfügbaren Buchstaben für das Bonuswort zurück.
    """
    
    def check_bonus_reveal_conditions(self) -> bool:
        """
    Prüft die Bedingungen für die Enthüllung neuer Buchstaben.
    """
    
    def can_reveal_new_letter(self) -> bool:
        """
    Überprüft ob ein neuer Buchstabe des Bonuswortes aufgedeckt werden kann.
    """
    return False


# LLM-SPEZIFISCHE INFORMATIONEN
class BonusWordConstraints:
    """
    Definiert die Einschränkungen für das Bonuswort.
    """
    
    def __init__(self):
        self.max_letters_per_word: int = 1
    self.max_bonus_length: int = 8  # Standard-Maximallänge
    
    def get_constraints_info(self) -> Dict[str, Any]:
    """
    Gibt Informationen über die maximal mögliche Länge des Bonuswortes.
    """
    
    def calculate_max_bonus_length(self, num_questions: int) -> int:
        """
    Berechnet die maximale Länge des Bonuswortes
    basierend auf der Anzahl der Fragen.
    """
    return min(num_questions * self.max_letters_per_word, 15)
    
    def get_bonus_word_hint(self) -> str:
        """
    Gibt dem LLM einen Hinweis für das Bonuswort.
    """
    
    def get_bonus_reveal_status(self) -> Dict[str, Any]:
    """
    Gibt den aktuellen Status der Bonuswort-Enthüllung zurück.
    """
    return {
        "available_letters": self.available_letters,
        "max_bonus_length": self.max_bonus_length
    }


# BEISPIEL FÜR LLMs
if __name__ == "__main__":
    """
    Beispiel für LLM-Informationen über das Bonuswort.
    """
    pass