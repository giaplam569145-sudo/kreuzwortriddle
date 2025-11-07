#!/usr/bin/env python3
"""Example for the bonus word feature in the Kreuzwort-Riddle Framework.

Demonstrates how an additional word can be derived from the intersection
points of the other words.

Author: Qwen Code (2025)
"""

from kreuzwortriddle import LLMKreuzwortAPI, BonusRevealSystem


def demonstrate_bonus_feature():
    """Shows how the bonus word is progressively revealed."""
    # Framework mit Bonuswort-Feature
    api = LLMKreuzwortAPI()
    bonus_system = BonusRevealSystem()

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
    print(f"Frage 2: {result2}")

    # Frage 3: Horizontal
    result3 = api.add_question(
        "Hauptstadt von Italien",
        "Rom",
        "horizontal"
    )
    print(f"Frage 3: {result3}")

    # Validierung
    validation = api.validate_all()
    print(f"\nValidierung: {validation}")

    # Generiere das Rätsel
    generation = api.generate()
    print(f"Generierung: {generation}")

    # Bonuswort definieren
    bonus_word = "EUROPA"
    bonus_description = "Der Kontinent zu dem alle Hauptstädte gehören"

    print("\n=== BONUSWORT-FEATURE ===\n")

    if generation["status"] == "success":
        # Setze das Bonuswort
        bonus_system.set_bonus_word(bonus_word)

        # Aktualisiere verfügbare Buchstaben aus dem Gitter
        bonus_system.update_available_letters(api.get_grid())

        print(f"Bonuswort gesetzt: {bonus_word}")
        print(f"Beschreibung: {bonus_description}")
        print(f"Anfangs-Status: {bonus_system.get_bonus_word_hint()}")

        # Das Bonuswort ergibt sich aus den Kreuzungspunkten der anderen Wörter
        print("\n=== BONUSWORT-LOGIK ===\n")
        print("Das Bonuswort 'EUROPA' wird Buchstabe für Buchstabe aufgedeckt:")
        print("- B von Berlin (Position 1,1)")
        print("- E von Paris (Position 2,1)")
        print("- U von Rom (Position 3,1)")

        # LLM-spezifische Hinweise für Bonuswort
        print("\n=== LLM-HINWEISE FÜR BONUSWORT ===\n")
        print("Bonuswort-Logik:")
        print("1. Das Bonuswort wird nicht direkt als Frage hinzugefügt")
        print("2. Es ergibt sich aus den Buchstaben an den Kreuzungspunkten")
        print("3. Sobald genug Buchstaben bekannt sind, kann das LLM")
        print("   das Bonuswort identifizieren und dem Benutzer als zusätzlichen Hinweis geben")

        # Progressive Enthüllung simulieren
        print("\n=== PROGRESSIVE ENTHÜLLUNG ===\n")

        for i in range(6):  # 6 Buchstaben in EUROPA
            if bonus_system.can_reveal_bonus_letter():
                letter = bonus_system.reveal_next_letter()
                print(f"Schritt {i+1}: Buchstabe '{letter}' aufgedeckt")
                print(f"Status: {bonus_system.get_bonus_word_hint()}")

                # LLM-Logik: Wenn genug Buchstaben bekannt sind, identifiziere das Wort
                revealed_count = len([l for l in bonus_system.revealed_letters if l != '_'])
                if revealed_count >= 3:
                    print(f"LLM-Hinweis: Mit {revealed_count} Buchstaben könnte das Bonuswort '{bonus_word}' sein")
            else:
                print(f"Schritt {i+1}: Keine weiteren Buchstaben verfügbar")
                break

        # Zeige das finale Gitter
        print("\n=== GENERIERTES GITTER ===\n")
        grid = api.get_grid()
        for row in grid:
            print(' '.join(cell if cell else '.' for cell in row))

        # Zeige Platzierungen
        placements = api.get_placements()
        print(f"\nPlatzierte Wörter: {len(placements)}")
        for placement in placements:
            print(f"- {placement['answer']} ({placement['orientation']}) an Position ({placement['x']},{placement['y']})")

        print(f"\nFinale Bonuswort-Info: {bonus_system.get_bonus_letter_info()}")

    else:
        print("Rätsel konnte nicht generiert werden - Bonuswort-Feature nicht verfügbar")

    print("\n=== FRAMEWORK MIT BONUSWORT FERTIG ===\n")


def demonstrate_bonus_word_constraints():
    """Demonstrates the constraints for bonus words."""
    from llm_bonus_info import BonusWordConstraints, get_bonus_word_guidelines

    print("=== BONUSWORT-EINSCHRÄNKUNGEN ===\n")

    constraints = BonusWordConstraints()

    # Zeige Constraint-Informationen
    print("Constraint-Informationen:")
    constraint_info = constraints.get_constraints_info()
    for key, value in constraint_info.items():
        print(f"- {key}: {value}")

    # Berechne maximale Bonuswort-Länge für verschiedene Anzahlen von Fragen
    print("\nMaximale Bonuswort-Längen:")
    for num_questions in [3, 5, 8, 10]:
        max_length = constraints.calculate_max_bonus_length(num_questions)
        print(f"- {num_questions} Fragen: maximal {max_length} Buchstaben")

    # Zeige Richtlinien
    print("\nLLM-Richtlinien:")
    guidelines = get_bonus_word_guidelines()
    print(f"- Zweck: {guidelines['purpose']}")
    print(f"- Mechanismus: {guidelines['mechanism']['progressive_reveal']}")

    print("\n=== EINSCHRÄNKUNGS-DEMO ABGESCHLOSSEN ===\n")


if __name__ == "__main__":
    demonstrate_bonus_feature()
    demonstrate_bonus_word_constraints()
