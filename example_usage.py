#!/usr/bin/env python3
"""
Beispiel-Nutzung des Kreuzwort-Riddle Frameworks für LLMs

Dieses Beispiel zeigt, wie LLMs das Framework nutzen koennen, um sich auf Fragen und Antworten zu konzentrieren.

Autor: Qwen Code (2025)
"""

from kreuzwortriddle import BonusRevealSystem, LLMKreuzwortAPI

# Framework initialisieren
print("=== KREUZWORT-RIDDLE FRAMEWORK BEISPIEL ===\n")

# API-Instanz erstellen
api = LLMKreuzwortAPI(width=15, height=15)

# Beispiel 1: Erfolgreiche Fragen
print("\n1. Erfolgreiche Fragen hinzufügen:")

# Frage 1
result1 = api.add_question(
    "Hauptstadt von Deutschland",
    "Berlin",
    "horizontal"
)
print(f"Ergebnis: {result1}")

# Frage 2
result2 = api.add_question(
    "Hauptstadt von Frankreich",
    "Paris",
    "vertical"
)
print(f"Ergebnis: {result2}")

# Frage 3
result3 = api.add_question(
    "Stadt in Tirol",
    "Innsbruck",
    "horizontal"
)
print(f"Ergebnis: {result3}")

# Validierung aller Fragen
print("\n2. Validierung aller Fragen:")
validation = api.validate_all()
print(f"Validierung: {validation}")

# Rätsel generieren
generation = api.generate()
print(f"Generierung: {generation}")

# Probleme identifizieren
print("\n3. Identifikation problematischer Fragen:")
problems = api.get_problems()
print(f"Probleme: {problems}")

print("\n=== FRAMEWORK STATUS ===\n")
print(f"Validierung: {validation}")
print(f"Generierung: {generation}")

# Beispiel 2: Problem mit "fauler" Frage
print("\n4. Beispiel mit problematischer Frage:")

# Diese Frage wird Probleme verursachen (kein gemeinsamer Buchstabe mit anderen):
result4 = api.add_question(
    "Japanische Kampf kunst",
    "Judo",
    "horizontal"
)
print(f"Ergebnis: {result4}")

# "Faul" — Q hat keine Überschneidung
result5 = api.add_question(
    "Sehr spezifisches Wort",
    "Quiz",
    "vertical"
)
print(f"Ergebnis: {result5}")

print("\n=== LLM-HINWEISE ===\n")
print("LLM: Wenn du Fehlermeldungen siehst wie:")
print("'Antwort hat keine gemeinsamen Buchstaben mit anderen Antworten'")

# Finale Validierung
final_validation = api.validate_all()
print(f"Finale Validierung: {final_validation}")

print("\n=== WICHTIGE FEHLERMELDUNGEN ===\n")

# LLM-spezifische Fehlermeldungen
print("\nTypische Fehlermeldungen fuer LLMs:")
print("- 'Frage-Text ist leer' -> Gib einen sinnvollen Fragetext ein")
print("- 'Antwort ist leer' -> Gib eine gueltige Antwort ein")
print("- 'Antwort muss mindestens 2 Buchstaben lang sein'")
print("- 'Antwort darf nur Buchstaben enthalten'")
print("- 'Antwort ist zu lang' -> Kuerze die Antwort")

# Beispiel 3: Bonuswort-System
print("\n=== BEISPIEL 3: BONUSWORT-SYSTEM ===\n")

bonus_system = BonusRevealSystem()
bonus_system.set_bonus_word("EUROPA")

if generation["status"] == "success":
    bonus_system.update_available_letters(api.get_grid())
    print(f"Bonuswort-Info: {bonus_system.get_bonus_letter_info()}")
    print(f"Bonuswort-Hinweis: {bonus_system.get_bonus_word_hint()}")

    # Simuliere Buchstaben-Enthüllung
    for i in range(3):
        if bonus_system.can_reveal_bonus_letter():
            letter = bonus_system.reveal_next_letter()
            print(f"Buchstabe aufgedeckt: {letter}")
            print(f"Status: {bonus_system.get_bonus_word_hint()}")

# Zeige das generierte Gitter
if generation["status"] == "success":
    print("\n=== GENERIERTES GITTER ===\n")
    grid = api.get_grid()
    placements = api.get_placements()

    for row in grid:
        print(' '.join(cell if cell else '.' for cell in row))

    print(f"\nPlatzierungen: {len(placements)} Wörter platziert")

print("\n=== FRAMEWORK ERFOLGREICH INITIALISIERT ===\n")
