#!/usr/bin/env python3
"""
Testfälle für das Kreuzwort-Riddle Framework

Print-basierte Tests mit Assertions.
"""

from kreuzwortriddle import LLMKreuzwortAPI, BonusRevealSystem, BonusWordConstraints, ValidationError

passed = 0
failed = 0


def assert_test(name: str, condition: bool, detail: str = ""):
    global passed, failed
    if condition:
        passed += 1
        print(f"  PASS: {name}")
    else:
        failed += 1
        msg = f"  FAIL: {name}"
        if detail:
            msg += f" — {detail}"
        print(msg)


def test_basic_validation():
    """Testet die grundlegende Validierungslogik"""
    print("=== TEST 1: GÜLTIGE FRAGEN ===\n")

    api = LLMKreuzwortAPI()

    result1 = api.add_question("Hauptstadt von Deutschland", "Berlin", "horizontal")
    assert_test("Gültige Frage hinzugefügt", result1["status"] == "success", str(result1))

    result2 = api.add_question("", "Test", "horizontal")
    assert_test("Leere Frage abgelehnt", result2["status"] == "error", str(result2))

    result3 = api.add_question("Hauptstadt von Frankreich", "Paris", "vertical")
    assert_test("Vertikale Frage hinzugefügt", result3["status"] == "success", str(result3))

    validation = api.validate_all()
    assert_test("Validierung OK", validation["status"] == "valid", str(validation))

    problems = api.get_problems()
    assert_test("Keine problematischen Fragen", problems["status"] == "no_problems", str(problems))

    generation = api.generate()
    assert_test("Generierung erfolgreich", generation["status"] == "success", str(generation))

    print("\n=== TEST 2: VALIDIERUNGSFEHLER ===\n")

    result4 = api.add_question("Frage mit Zahlen", "Test123", "horizontal")
    assert_test("Nicht-alphabetische Antwort abgelehnt", result4["status"] == "error")

    result5 = api.add_question("Zu kurze Antwort", "A", "horizontal")
    assert_test("Zu kurze Antwort abgelehnt", result5["status"] == "error")

    result6 = api.add_question("Zu lange Antwort", "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "horizontal")
    assert_test("Zu lange Antwort abgelehnt", result6["status"] == "error")


def test_bonus_system():
    """Testet das Bonuswort-System"""
    print("\n=== TEST 3: BONUSWORT-SYSTEM ===\n")

    bonus_system = BonusRevealSystem()
    bonus_system.set_bonus_word("EUROPA")

    assert_test("Bonuswort gesetzt", bonus_system.bonus_word == "EUROPA")
    assert_test("Hint zeigt Unterstriche", "_" in bonus_system.get_bonus_word_hint())

    sim_grid = [
        ['', 'E', '', '', '', ''],
        ['', '', '', '', '', ''],
        ['U', '', 'R', '', '', ''],
        ['', '', '', '', 'O', ''],
        ['', 'P', '', 'A', '', ''],
        ['', '', '', '', '', ''],
    ]
    bonus_system.update_available_letters(sim_grid)

    assert_test("available_letters nicht leer", len(bonus_system.available_letters) > 0,
                f"available_letters: {bonus_system.available_letters}")
    assert_test("can_reveal_bonus_letter ist True", bonus_system.can_reveal_bonus_letter())

    letter1 = bonus_system.reveal_next_letter()
    assert_test("Erster Buchstabe aufgedeckt", letter1 is not None, f"letter={letter1}")
    assert_test("revealed_positions befüllt", len(bonus_system.revealed_positions) > 0,
                f"positions: {bonus_system.revealed_positions}")

    letter2 = bonus_system.reveal_next_letter()
    assert_test("Zweiter Buchstabe aufgedeckt", letter2 is not None, f"letter={letter2}")

    letter3 = bonus_system.reveal_next_letter()
    assert_test("Dritter Buchstabe aufgedeckt", letter3 is not None, f"letter={letter3}")

    print(f"  Bonuswort-Status: {bonus_system.get_bonus_word_hint()}")


def test_grid_generation():
    """Testet die Gitter-Generierung"""
    print("\n=== TEST 4: GITTER-GENERIERUNG ===\n")

    api = LLMKreuzwortAPI(width=15, height=15)

    questions = [
        ("Hauptstadt von Deutschland", "Berlin", "horizontal"),
        ("Fluss in Deutschland", "Elbe", "vertical"),
        ("Bundesland", "Bayern", "horizontal"),
        ("Gebirge", "Alpen", "vertical")
    ]

    for question, answer, orientation in questions:
        result = api.add_question(question, answer, orientation)
        assert_test(f"Frage '{answer}' hinzugefügt", result["status"] == "success")

    generation = api.generate()
    assert_test("Gitter-Generierung erfolgreich", generation["status"] == "success",
                str(generation))

    if generation["status"] == "success":
        grid = api.get_grid()
        placements = api.get_placements()

        assert_test("Alle 4 Wörter platziert", len(placements) == 4,
                    f"nur {len(placements)} platziert")

        print("\n  Gitter:")
        for row in grid:
            print('  ' + ' '.join(cell if cell else '.' for cell in row))

        print(f"\n  Platzierungen: {len(placements)}")
        for p in placements:
            print(f"  - {p['answer']} ({p['orientation']}) an ({p['x']},{p['y']})")


def test_constraints():
    """Testet BonusWordConstraints"""
    print("\n=== TEST 5: BONUSWORT-EINSCHRÄNKUNGEN ===\n")

    constraints = BonusWordConstraints()

    assert_test("max_bonus_length=8", constraints.max_bonus_length == 8)
    assert_test("min_bonus_length=3", constraints.min_bonus_length == 3)
    assert_test("calculate_max(5)=5", constraints.calculate_max_bonus_length(5) == 5)
    assert_test("calculate_max(2)=3", constraints.calculate_max_bonus_length(2) == 3)

    errors = constraints.validate_bonus_word("EUROPA", {'E', 'U', 'R', 'O', 'P', 'A'})
    assert_test("Gültiges Bonuswort", len(errors) == 0, str(errors))

    errors = constraints.validate_bonus_word("XYZ", {'E', 'U', 'R'})
    assert_test("Ungültiges Bonuswort erkannt", len(errors) > 0, str(errors))


if __name__ == "__main__":
    test_basic_validation()
    test_bonus_system()
    test_grid_generation()
    test_constraints()

    print(f"\n{'='*50}")
    print(f"ERGEBNIS: {passed} bestanden, {failed} fehlgeschlagen")
    print(f"{'='*50}")

    if failed > 0:
        exit(1)
