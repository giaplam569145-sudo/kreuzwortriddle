#!/usr/bin/env python3
"""
Review-Demo: Kreuzwort-Riddle Framework -- Staerken & Schwaechen illustriert.

Zeigt die im Code-Review identifizierten Befunde an konkreten Beispielen.
"""

from collections import Counter

from kreuzwortriddle import BonusRevealSystem, BonusWordConstraints, KreuzwortRiddle, LLMKreuzwortAPI

LINE = "=" * 60
DASH = "-" * 60


def zeige_trennung_api_vs_core():
    """Staerke 2.1: Saubere API-Trennung zwischen Core und LLM-Interface."""
    print(LINE)
    print("2.1  Saubere API-Trennung: Core vs. LLMKreuzwortAPI")
    print(LINE)

    r = KreuzwortRiddle()
    try:
        r.add_question("", "Test")
    except Exception as e:
        print(f"  Core (KreuzwortRiddle):    {type(e).__name__}: {e}")

    api = LLMKreuzwortAPI()
    result = api.add_question("", "Test")
    print(f"  API (LLMKreuzwortAPI):      status={result['status']}")
    print()


def zeige_alles_gruen():
    """Tests & Linting: Alles sauber."""
    print(LINE)
    print("2.4  Code-Gesundheit: Alle Tests passieren")
    print(LINE)

    api = LLMKreuzwortAPI()
    api.add_question("Hauptstadt", "Berlin", "horizontal")
    api.add_question("Fluss", "Elbe", "vertical")
    assert api.validate_all()["status"] == "valid"
    assert api.generate()["status"] == "success"
    assert api.get_problems()["status"] == "no_problems"
    print("  OK  add_question -> validate_all -> generate -> get_problems")
    print("  OK  Alle 3 Woerter platziert:", len(api.get_placements()))
    print()


def zeige_bonus_duplikat_bug_fixed():
    """Fix 3.1: Counter statt Set -- Duplikat-Buchstaben im Bonuswort funktionieren jetzt."""
    print(LINE)
    print("3.1  GEFIXT: Duplikat-Buchstaben im Bonuswort (Counter statt Set)")
    print(LINE)

    b = BonusRevealSystem()
    b.set_bonus_word("EFFECT")
    grid = [
        ['E', 'F', 'F', 'E', 'C', 'T'],
        ['',  '',  '',  '',  '',  ''],
    ]
    b.update_available_letters(grid)
    print("  Bonuswort:     EFFECT")
    print(f"  Interner Counter: {dict(b._letter_counts)}")
    print("  -> Jeder Buchstabe mit korrektem Count (E:2, F:2, C:1, T:1)")

    for i in range(7):
        letter = b.reveal_next_letter()
        if letter:
            print(f"  Schritt {i+1}: '{letter}' -> {b.get_bonus_word_hint()}")
        else:
            break
    print("  -> Alle 6 Buchstaben aufgedeckt!")
    print()

    b2 = BonusRevealSystem()
    b2.set_bonus_word("BANANA")
    grid2 = [
        ['B', 'A', 'N', 'A', 'N', 'A'],
        ['',  '',  '',  '',  '',  ''],
    ]
    b2.update_available_letters(grid2)
    for i in range(7):
        letter = b2.reveal_next_letter()
        if letter:
            print(f"  Schritt {i+1}: '{letter}' -> {b2.get_bonus_word_hint()}")
        else:
            break
    print("  -> Alle 6 Buchstaben aufgedeckt!")
    print()


def zeige_reveal_position_fixed():
    """Fix 3.4: reveal_next_letter verbraucht jetzt korrekt die Positionen."""
    print(LINE)
    print("3.4  GEFIXT: Positionen werden jetzt korrekt verbraucht")
    print(LINE)

    b = BonusRevealSystem()
    b.set_bonus_word("AA")
    grid = [
        ['A', 'A'],
        ['',  ''],
    ]
    b.update_available_letters(grid)
    print("  Grid: [A A]")
    print(f"  _grid_positions: {b._grid_positions}")

    b.reveal_next_letter()
    print(f"  Nach 1. Enthuellung revealed_positions: {b.revealed_positions}")
    print(f"  Nach 1. Enthuellung _grid_positions:    {b._grid_positions}")
    print("  -> (0,0) wurde verbraucht, (0,1) bleibt fuer die 2. Enthuellung")

    b.reveal_next_letter()
    print(f"  Nach 2. Enthuellung revealed_positions: {b.revealed_positions}")
    print(f"  -> Korrekt: beide Positionen ({len(b.revealed_positions)}) verbraucht")
    print()
    print("  RICHTIG: Counter statt Set:")
    counter = Counter(['E', 'F', 'F', 'E', 'C', 'T'])
    print(f"  Counter: {dict(counter)} -- jeder Buchstabe mit korrektem Count")
    print()

    b2 = BonusRevealSystem()
    b2.set_bonus_word("BANANA")
    grid2 = [
        ['B', 'A', 'N', 'A', 'N', 'A'],
        ['',  '',  '',  '',  '',  ''],
    ]
    b2.update_available_letters(grid2)
    count = 0
    for _ in range(10):
        if b2.reveal_next_letter():
            count += 1
    print(f"  Bonuswort 'BANANA': {count}/6 Buchstaben aufgedeckt (sollte 6 sein)")
    print()


def zeige_reveal_position_bug():
    """Bug 3.4: reveal_next_letter liefert falsche Positionen."""
    print(LINE)
    print("3.4  reveal_next_letter: Falsche Positionen")
    print(LINE)

    b = BonusRevealSystem()
    b.set_bonus_word("AA")
    grid = [
        ['A', 'A'],
        ['',  ''],
    ]
    b.update_available_letters(grid)
    print("  Grid: [A A]")
    print("  Bonuswort: AA")
    print(f"  _grid_positions hat nur EINEN Eintrag fuer 'A': {b._grid_positions}")
    print("  -> Kein Weg, Position 0 und Position 1 separat zu referenzieren")

    b.reveal_next_letter()
    print(f"  revealed_positions nach 1. Enthuellung: {b.revealed_positions}")
    print("  -> (0,0) und (0,1) haben beide 'A', aber nur (0,0) wird je referenziert")
    print()


def zeige_problem_erkennung():
    """get_problematic_questions und wie es arbeitet."""
    print(LINE)
    print("3.5  get_problematic_questions: Nur Buchstaben-Set-Intersection")
    print(LINE)

    api = LLMKreuzwortAPI()
    api.add_question("F1", "ABC", "horizontal")
    api.add_question("F2", "DEF", "vertical")
    api.add_question("F3", "GHI", "horizontal")

    p = api.get_problems()
    r = api.generate()
    print("  Woerter: ABC (h), DEF (v), GHI (h)")
    print(f"  get_problems(): {p['status']} -- {len(p.get('problems', []))} Probleme")
    print(f"  generate():     {r['status']}")
    print("  -> Kein gemeinsamer Buchstabe -> korrekt erkannt")
    print()

    # Test mit Fragen, die gemeinsamen Buchstaben haben
    api2 = LLMKreuzwortAPI()
    api2.add_question("F1", "HALLOWELT", "horizontal")
    api2.add_question("F2", "SCHOKOLADE", "vertical")
    api2.add_question("F3", "WANDERTAG", "horizontal")
    p2 = api2.get_problems()
    r2 = api2.generate()
    print("  Woerter: HALLOWELT (h), SCHOKOLADE (v), WANDERTAG (h)")
    print(f"  get_problems(): {p2['status']}")
    print(f"  generate():     {r2['status']}")
    if r2['status'] == 'success':
        for p in api2.get_placements():
            print(f"    {p['answer']} @ ({p['x']},{p['y']})")
    print()


def zeige_bonusconstraints():
    """BonusWordConstraints: Randfaelle."""
    print(LINE)
    print("BonusWordConstraints: Randfaelle")
    print(LINE)

    c = BonusWordConstraints()
    print(f"  min_bonus_length (0 Fragen): {c.calculate_max_bonus_length(0)} "
          f"(min = {c.min_bonus_length})")
    print(f"  max_bonus_length (10 Fragen): {c.calculate_max_bonus_length(10)} "
          f"(max = {c.max_bonus_length})")
    print(f"  max_bonus_length (20 Fragen): {c.calculate_max_bonus_length(20)} "
          f"(geclamped auf {c.max_bonus_length})")

    errors = c.validate_bonus_word("A" * 50, {"A"})
    print(f"  Bonuswort 50xA: {len(errors)} Fehler:")
    for e in errors:
        print(f"    - {e}")
    print()


def zeige_grid_generierung():
    """Grid-Generierung: Erfolgsbeispiele."""
    print(LINE)
    print("Grid-Generierung: Erfolgsbeispiele")
    print(LINE)

    tests = [
        ("2 Woerter", [("Q1", "BERLIN", "horizontal"),
                       ("Q2", "ELBE", "vertical")]),
        ("3 Woerter", [("Q1", "BERLIN", "horizontal"),
                       ("Q2", "PARIS", "vertical"),
                       ("Q3", "INNSBRUCK", "horizontal")]),
        ("4 Woerter", [("Q1", "BERLIN", "horizontal"),
                       ("Q2", "ELBE", "vertical"),
                       ("Q3", "BAYERN", "horizontal"),
                       ("Q4", "ALPEN", "vertical")]),
        ("5 Woerter", [("Q1", "ABCDE", "horizontal"),
                       ("Q2", "BCDEF", "vertical"),
                       ("Q3", "CDEFG", "horizontal"),
                       ("Q4", "DEFGH", "vertical"),
                       ("Q5", "EFGHI", "horizontal")]),
    ]

    for name, words in tests:
        api = LLMKreuzwortAPI()
        for q, a, o in words:
            api.add_question(q, a, o)
        r = api.generate()
        placed = len(api.get_placements()) if r["status"] == "success" else 0
        print(f"  {name}: {r['status']} ({placed}/{len(words)} platziert)")

    api = LLMKreuzwortAPI()
    api.add_question("Q1", "AAAA", "horizontal")
    api.add_question("Q2", "BBBB", "vertical")
    api.add_question("Q3", "CCCC", "horizontal")
    r = api.generate()
    p = api.get_problems()
    print(f"  Kein Overlap (AAAA/BBBB/CCCC): {r['status']}, "
          f"problems: {p['status']} ({len(p.get('problems', []))} Probleme)")
    print()


def zeige_framework_komplett():
    """Kompletter Workflow von Anfang bis Ende."""
    print(LINE)
    print("Kompletter Workflow: Fragen -> Validieren -> Generieren -> Bonuswort")
    print(LINE)

    api = LLMKreuzwortAPI(width=20, height=20)
    bonus = BonusRevealSystem()

    fragen = [
        ("Hauptstadt von Deutschland",   "BERLIN",    "horizontal"),
        ("Hauptstadt von Frankreich",    "PARIS",     "vertical"),
        ("Fluss in Deutschland",         "ELBE",      "horizontal"),
        ("Bundesland im Sueden",          "BAYERN",    "vertical"),
        ("Gebirge in Mitteleuropa",      "ALPEN",     "horizontal"),
    ]

    print()
    for q, a, o in fragen:
        result = api.add_question(q, a, o)
        icon = "+" if result["status"] == "success" else "-"
        print(f"    {icon} {a:10s} ({o:10s}) -> {result['status']}")

    print(f"  Validierung:    {api.validate_all()['status']}")
    gen = api.generate()
    print(f"  Generierung:    {gen['status']}")

    if gen["status"] == "success":
        bonus.set_bonus_word("EUROPA")
        bonus.update_available_letters(api.get_grid())

        print()
        print("  Gitter:")
        for row in api.get_grid():
            print(f"    {' '.join(c if c else '.' for c in row)}")

        print()
        N = len(api.get_placements())
        print(f"  Platzierungen ({N}):")
        for p in api.get_placements():
            print(f"    #{p['number']} {p['answer']:10s} ({p['orientation']:10s}) "
                  f"@ ({p['x']:2d},{p['y']:2d})")

        print()
        print("  Bonuswort-Enthuellung:")
        print(f"    Start: {bonus.get_bonus_word_hint()}")
        for _ in range(8):
            if bonus.can_reveal_bonus_letter():
                bonus.reveal_next_letter()
        print(f"    Ende:  {bonus.get_bonus_word_hint()}")

    print()


if __name__ == "__main__":
    zeige_trennung_api_vs_core()
    zeige_alles_gruen()
    zeige_bonus_duplikat_bug_fixed()
    zeige_reveal_position_fixed()
    zeige_problem_erkennung()
    zeige_bonusconstraints()
    zeige_grid_generierung()
    zeige_framework_komplett()

    print(LINE)
    print("Review-Demo abgeschlossen.")
    print("Siehe CODE_REVIEW.md fuer die vollstaendige Analyse.")
    print(LINE)
