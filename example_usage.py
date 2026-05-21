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

# Gitter und Platzierungen fuer spaetere Anzeige sichern
saved_grid = api.get_grid() if generation["status"] == "success" else None
saved_placements = api.get_placements() if generation["status"] == "success" else None

# Probleme identifizieren
print("\n3. Identifikation problematischer Fragen:")
problems = api.get_problems()
print(f"Probleme: {problems}")

print("\n=== FRAMEWORK STATUS ===\n")
print(f"Validierung: {validation}")
print(f"Generierung: {generation}")

# Beispiel 2: Problem mit "fauler" Frage
print("\n4. Beispiel mit problematischer Frage:")

# Diese Fragen verursachen Probleme — sie haben keine gemeinsamen Buchstaben:
result4 = api.add_question(
    "Japanische Kampfkunst",
    "Judo",
    "horizontal"
)
print(f"Ergebnis: {result4}")

result5 = api.add_question(
    "Sehr spezifisches Wort",
    "Quiz",
    "vertical"
)
print(f"Ergebnis: {result5}")

# get_problems() erkennt jetzt, welche Antworten keine Ueberschneidung haben
print("\n5. Problemerkennung nach Hinzufuegen:")
problems = api.get_problems()
print(f"Probleme: {problems}")

# Erneute Generierung (wird vermutlich fehlschlagen wegen fehlender Kreuzungen)
regen = api.generate()
print(f"Erneute Generierung: {regen}")

print("\n=== LLM-HINWEISE ===\n")
print("LLM: Wenn du Fehlermeldungen siehst wie:")
print("'Antwort hat keine gemeinsamen Buchstaben mit anderen Antworten'")

final_validation = api.validate_all()
print(f"Finale Validierung: {final_validation}")

print("\n=== WICHTIGE FEHLERMELDUNGEN ===\n")

print("\nTypische Fehlermeldungen fuer LLMs:")
print("- 'Frage-Text ist leer' -> Gib einen sinnvollen Fragetext ein")
print("- 'Antwort ist leer' -> Gib eine gueltige Antwort ein")
print("- 'Antwort muss mindestens 2 Buchstaben lang sein'")
print("- 'Antwort darf nur Buchstaben enthalten'")
print("- 'Antwort ist zu lang' -> Kuerze die Antwort")

# Beispiel 3: Bonuswort-System (nutzt das erste erfolgreiche Gitter)
print("\n=== BEISPIEL 3: BONUSWORT-SYSTEM ===\n")

bonus_system = BonusRevealSystem()
bonus_system.set_bonus_word("EUROPA")

if saved_grid:
    bonus_system.update_available_letters(saved_grid)
    print(f"Bonuswort-Info: {bonus_system.get_bonus_letter_info()}")
    print(f"Bonuswort-Hinweis: {bonus_system.get_bonus_word_hint()}")

    for _ in range(3):
        if bonus_system.can_reveal_bonus_letter():
            letter = bonus_system.reveal_next_letter()
            print(f"Buchstabe aufgedeckt: {letter}")
            print(f"Status: {bonus_system.get_bonus_word_hint()}")
else:
    print("Kein erfolgreiches Gitter fuer Bonuswort verfuegbar")

if saved_grid:
    print("\n=== GENERIERTES GITTER ===\n")
    for row in saved_grid:
        print(' '.join(cell if cell else '.' for cell in row))

    print(f"\nPlatzierungen: {len(saved_placements)} Woerter platziert")

print("\n=== FRAMEWORK ERFOLGREICH INITIALISIERT ===\n")
