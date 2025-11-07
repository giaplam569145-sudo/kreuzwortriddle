#!/usr/bin/env python3
"""Test cases for the Kreuzwort-Riddle Framework.

These tests demonstrate the LLM-friendly API and automatic validation.
"""

from kreuzwortriddle import LLMKreuzwortAPI, ValidationError


def test_basic_validation():
    """Tests the basic validation logic of the framework."""
    api = LLMKreuzwortAPI()

    # Test 1: Gültige Fragen
    print("=== TEST 1: GÜLTIGE FRAGEN ===\n")

    # Erfolgreiche Fragen
    result1 = api.add_question(
        "Hauptstadt von Deutschland",
        "Berlin",
        "horizontal"
    )
    print(f"Test 1 - Gültige Frage: {result1}")

    # Test 2: Ungültige Frage (leer)
    result2 = api.add_question("", "Test", "horizontal")
    print(f"Test 2 - Ungültige Frage (leer): {result2}")

    # Test 3: Problem mit Überschneidungen
    result3 = api.add_question(
        "Hauptstadt von Frankreich",
        "Paris",
        "vertical"
    )
    print(f"Test 3 - Gültige vertikale Frage: {result3}")

    # Validierung
    validation = api.validate_all()
    print(f"Validierungsergebnis: {validation}")

    # Test 4: Identifikation "fauler" Fragen
    problems = api.get_problems()
    print(f"Identifizierte Probleme: {problems}")

    # Test 5: Generierung
    generation = api.generate()
    print(f"Generierungsergebnis: {generation}")

    print("\n=== TEST 2: VALIDIERUNGSFEHLER ===\n")

    # Ungültige Fragen testen
    print("\n=== TEST 2: UNGÜLTIGE FRAGEN ===\n")

    # Diese Tests zeigen die LLM-freundliche Fehlerbehandlung

    # Test mit nicht-alphabetischen Zeichen
    result4 = api.add_question(
        "Frage mit Zahlen",
        "Test123",
        "horizontal"
    )
    print(f"Test 4 - Ungültige Antwort (mit Zahlen): {result4}")

    # Test mit zu kurzer Antwort
    result5 = api.add_question(
        "Zu kurze Antwort",
        "A",
        "horizontal"
    )
    print(f"Test 5 - Zu kurze Antwort: {result5}")

    # Test mit zu langer Antwort
    result6 = api.add_question(
        "Zu lange Antwort",
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "horizontal"
    )
    print(f"Test 6 - Zu lange Antwort: {result6}")

    print("\n=== FRAMEWORK TEST ABGESCHLOSSEN ===\n")


def test_bonus_system():
    """Tests the bonus word system."""
    from kreuzwortriddle import BonusRevealSystem

    print("=== TEST 3: BONUSWORT-SYSTEM ===\n")

    bonus_system = BonusRevealSystem()
    bonus_system.set_bonus_word("EUROPA")

    print(f"Bonuswort gesetzt: {bonus_system.get_bonus_word_hint()}")

    # Simuliere einige verfügbare Buchstaben
    bonus_system.available_letters = {'E', 'U', 'R', 'O', 'P', 'A'}

    print(f"Kann Buchstabe aufdecken: {bonus_system.can_reveal_bonus_letter()}")

    # Decke Buchstaben auf
    for i in range(3):
        letter = bonus_system.reveal_next_letter()
        print(f"Buchstabe aufgedeckt: {letter}")
        print(f"Status: {bonus_system.get_bonus_word_hint()}")

    print("\n=== BONUSWORT-TEST ABGESCHLOSSEN ===\n")


def test_grid_generation():
    """Tests the grid generation."""
    print("=== TEST 4: GITTER-GENERIERUNG ===\n")

    api = LLMKreuzwortAPI(width=10, height=10)

    # Füge Fragen hinzu, die sich kreuzen können
    questions = [
        ("Hauptstadt von Deutschland", "Berlin", "horizontal"),
        ("Fluss in Deutschland", "Elbe", "vertical"),
        ("Bundesland", "Bayern", "horizontal"),
        ("Gebirge", "Alpen", "vertical")
    ]

    for question, answer, orientation in questions:
        result = api.add_question(question, answer, orientation)
        print(f"Frage hinzugefügt: {result}")

    # Generiere das Gitter
    generation = api.generate()
    print(f"Generierung: {generation}")

    if generation["status"] == "success":
        grid = api.get_grid()
        placements = api.get_placements()

        print("\nGitter:")
        for row in grid:
            print(' '.join(cell if cell else '.' for cell in row))

        print(f"\nPlatzierungen: {placements}")

    print("\n=== GITTER-GENERIERUNG-TEST ABGESCHLOSSEN ===\n")


if __name__ == "__main__":
    test_basic_validation()
    test_bonus_system()
    test_grid_generation()
