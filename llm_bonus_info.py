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
    2. LLM kann Bonuswort-Logik verstehen
    3. LLM kann progressive Enthüllung steuern
    """
    
    def __init__(self):
        self.available_letters: Set[str] = set()
        self.max_bonus_length: int = 0
        self.revealed_letters: List[str] = []
        self.bonus_word: str = ""
        
    def update_bonus_info(self, current_grid: List[List[str]]) -> None:
        """
        Aktualisiert die Informationen über verfügbare Buchstaben für das Bonuswort.
        
        Args:
            current_grid: Das aktuelle Gitter mit platzierten Wörtern
        """
        self.available_letters.clear()
        
        # Sammle alle Buchstaben aus dem Gitter
        for row in current_grid:
            for cell in row:
                if cell and cell.isalpha():
                    self.available_letters.add(cell.upper())
    
    def get_available_letters(self) -> Set[str]:
        """
        Gibt die aktuell verfügbaren Buchstaben für das Bonuswort zurück.
        
        Returns:
            Set von verfügbaren Buchstaben
        """
        return self.available_letters.copy()
    
    def check_bonus_reveal_conditions(self) -> bool:
        """
        Prüft die Bedingungen für die Enthüllung neuer Buchstaben.
        
        Returns:
            True wenn Bedingungen erfüllt sind, False sonst
        """
        return (len(self.available_letters) > 0 and 
                len(self.revealed_letters) < len(self.bonus_word))
    
    def can_reveal_new_letter(self) -> bool:
        """
        Überprüft ob ein neuer Buchstabe des Bonuswortes aufgedeckt werden kann.
        
        Returns:
            True wenn ein neuer Buchstabe aufgedeckt werden kann
        """
        if not self.bonus_word:
            return False
            
        # Finde den nächsten nicht aufgedeckten Buchstaben
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                return letter in self.available_letters
        
        return False
    
    def set_bonus_word(self, word: str) -> None:
        """
        Setzt das Bonuswort und initialisiert die Enthüllung.
        
        Args:
            word: Das Bonuswort
        """
        self.bonus_word = word.upper()
        self.revealed_letters = ['_'] * len(word)
        self.max_bonus_length = len(word)
    
    def reveal_next_letter(self) -> Optional[str]:
        """
        Deckt den nächsten verfügbaren Buchstaben auf.
        
        Returns:
            Der aufgedeckte Buchstabe oder None
        """
        if not self.can_reveal_new_letter():
            return None
        
        # Finde den nächsten aufdeckbaren Buchstaben
        for i, letter in enumerate(self.bonus_word):
            if i >= len(self.revealed_letters) or self.revealed_letters[i] == '_':
                if letter in self.available_letters:
                    if i < len(self.revealed_letters):
                        self.revealed_letters[i] = letter
                    else:
                        self.revealed_letters.append(letter)
                    return letter
        
        return None
    
    def get_bonus_word_hint(self) -> str:
        """
        Gibt einen Hinweis für das Bonuswort zurück.
        
        Returns:
            String mit dem aktuellen Stand des Bonuswortes
        """
        if not self.bonus_word:
            return "Kein Bonuswort gesetzt"
        
        revealed = ''.join(self.revealed_letters)
        return f"Bonuswort: {revealed} ({len([l for l in self.revealed_letters if l != '_'])}/{len(self.bonus_word)} Buchstaben)"
    
    def get_bonus_statistics(self) -> Dict[str, Any]:
        """
        Gibt Statistiken über das Bonuswort zurück.
        
        Returns:
            Dict mit Statistiken
        """
        return {
            "bonus_word": self.bonus_word,
            "bonus_word_length": len(self.bonus_word),
            "available_letters": list(self.available_letters),
            "revealed_letters": self.revealed_letters,
            "revealed_count": len([l for l in self.revealed_letters if l != '_']),
            "can_reveal_more": self.can_reveal_new_letter(),
            "completion_percentage": (len([l for l in self.revealed_letters if l != '_']) / len(self.bonus_word) * 100) if self.bonus_word else 0
        }


# LLM-SPEZIFISCHE INFORMATIONEN
class BonusWordConstraints:
    """
    Definiert die Einschränkungen für das Bonuswort.
    """
    
    def __init__(self):
        self.max_letters_per_word: int = 1
        self.max_bonus_length: int = 8  # Standard-Maximallänge
        self.min_bonus_length: int = 3
    
    def get_constraints_info(self) -> Dict[str, Any]:
        """
        Gibt Informationen über die maximal mögliche Länge des Bonuswortes.
        
        Returns:
            Dict mit Constraint-Informationen
        """
        return {
            "max_letters_per_word": self.max_letters_per_word,
            "max_bonus_length": self.max_bonus_length,
            "min_bonus_length": self.min_bonus_length,
            "description": "Maximal ein Buchstabe pro Wort für das Bonuswort"
        }
    
    def calculate_max_bonus_length(self, num_questions: int) -> int:
        """
        Berechnet die maximale Länge des Bonuswortes basierend auf der Anzahl der Fragen.
        
        Args:
            num_questions: Anzahl der Fragen im Rätsel
            
        Returns:
            Maximale Länge des Bonuswortes
        """
        calculated = min(num_questions * self.max_letters_per_word, self.max_bonus_length)
        return max(calculated, self.min_bonus_length)
    
    def validate_bonus_word(self, bonus_word: str, available_letters: Set[str]) -> List[str]:
        """
        Validiert ein Bonuswort gegen die verfügbaren Buchstaben.
        
        Args:
            bonus_word: Das zu validierende Bonuswort
            available_letters: Verfügbare Buchstaben
            
        Returns:
            Liste von Validierungsfehlern
        """
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
        
        # Prüfe ob alle Buchstaben verfügbar sind
        word_letters = set(bonus_word.upper())
        missing_letters = word_letters - available_letters
        
        if missing_letters:
            errors.append(f"Fehlende Buchstaben im Gitter: {', '.join(missing_letters)}")
        
        return errors


def get_bonus_word_guidelines() -> Dict[str, Any]:
    """
    Gibt dem LLM klare Richtlinien für das Bonuswort.
    
    Returns:
        Dict mit Richtlinien
    """
    return {
        "purpose": "Das Bonuswort ergibt sich aus den Kreuzungspunkten der anderen Wörter",
        "constraints": {
            "max_letters_per_word": "Maximal ein Bonuswortbuchstabe pro Wort",
            "max_total_length": "Maximal 8 Buchstaben für das gesamte Bonuswort",
            "min_total_length": "Mindestens 3 Buchstaben für das Bonuswort"
        },
        "mechanism": {
            "progressive_reveal": "Das Bonuswort wird Buchstabe für Buchstabe aufgedeckt",
            "crossing_points": "Buchstaben stammen aus den Kreuzungspunkten der Wörter",
            "llm_role": "LLM identifiziert das Bonuswort wenn genug Buchstaben bekannt sind"
        },
        "examples": [
            {
                "words": ["Berlin", "Paris", "Rom"],
                "bonus_word": "EUROPA",
                "explanation": "Alle Hauptstädte gehören zum gleichen Kontinent"
            }
        ]
    }


# BEISPIEL FÜR LLMs
if __name__ == "__main__":
    """
    Beispiel für LLM-Informationen über das Bonuswort.
    """
    
    # Erstelle Bonus-Info-System
    bonus_info = LLMBonusInfo()
    constraints = BonusWordConstraints()
    
    # Beispiel-Gitter
    example_grid = [
        ['B', 'E', 'R', 'L', 'I', 'N'],
        ['E', '.', '.', '.', '.', '.'],
        ['R', '.', 'P', 'A', 'R', 'I'],
        ['L', '.', '.', '.', '.', 'S'],
        ['I', '.', '.', '.', '.', '.'],
        ['N', '.', '.', '.', '.', '.']
    ]
    
    # Aktualisiere verfügbare Buchstaben
    bonus_info.update_bonus_info(example_grid)
    
    # Setze Bonuswort
    bonus_info.set_bonus_word("EUROPA")
    
    print("=== BONUSWORT-INFORMATIONEN FÜR LLMs ===\n")
    
    print(f"Verfügbare Buchstaben: {bonus_info.get_available_letters()}")
    print(f"Bonuswort-Hinweis: {bonus_info.get_bonus_word_hint()}")
    print(f"Kann Buchstabe aufdecken: {bonus_info.can_reveal_new_letter()}")
    
    # Decke Buchstaben auf
    for i in range(3):
        letter = bonus_info.reveal_next_letter()
        if letter:
            print(f"Buchstabe aufgedeckt: {letter}")
            print(f"Status: {bonus_info.get_bonus_word_hint()}")
    
    print(f"\nStatistiken: {bonus_info.get_bonus_statistics()}")
    print(f"\nRichtlinien: {get_bonus_word_guidelines()}")