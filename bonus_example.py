#!/usr/bin/env python3
"""
Beispiel für die Bonuswort-Feature im Kreuzwort-Riddle Framework

Demonstriert wie ein zusätzliches Wort sich aus den Kreuzungspunkten der anderen Wörter ergibt.

Autor: Qwen Code (2025)
"""

from kreuzwortriddle import LLMKreuzwortAPI

def demonstrate_bonus_feature():
    """
    Zeigt wie das Bonuswort nach und nach aufgedeckt wird.
"""

# Framework mit Bonuswort-Feature
api = LLMKreuzwortAPI()

# Standardfragen hinzufügen
print("=== STANDARDFRAGEN ===\n")

# Frage 1: Horizontal
result1 = api.add_question(
    "Hauptstadt von Deutschland",
    "Berlin",
    "horizontal"
)
print(f"Frage 1: {result1}")

# Frage 2: Vertikal
result2 = api.add_question(
    "Hauptstadt von Frankreich",
    "Paris",
    "vertical"
)

# Frage 3: Horizontal  
result3 = api.add_question(
    "Hauptstadt von Italien",
    "Rom",
    "horizontal"
)

# Validierung
validation = api.validate_all()
print(f"Validierung: {validation}")

# Bonuswort definieren
bonus_word = "EUROPA"
bonus_description = "Der Kontinent zu dem alle Hauptstädte gehören")

print("\n=== BONUSWORT-FEATURE ===\n")

# Das Bonuswort ergibt sich aus den Kreuzungspunkten:")
print("- B von Berlin (Position 1,1)")
print("- E von Paris (Position 2,1)")
print("- U von Rom (Position 3,1)")

# LLM-spezifische Hinweise für Bonuswort
print("\n=== LLM-HINWEISE FÜR BONUSWORT ===\n")

# Bonuswort-Logik:
# 1. Das Bonuswort wird nicht direkt als Frage hinzugefügt
# 2. Es ergibt sich aus den Buchstaben an den Kreuzungspunkten.")

print("\n=== PROGRESSIVE ENTHÜLLUNG ===\n")
print("Das Bonuswort 'EUROPA' wird Buchstabe für Buchstabe aufgedeckt
# 3. Sobald genug Buchstaben bekannt sind, kann das LLM
#    das Bonuswort identifizieren und dem Benutzer als zusätzlichen Hinweis geben.")

print("\n=== FRAMEWORK MIT BONUSWORT FERTIG ===\n")