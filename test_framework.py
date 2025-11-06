#!/usr/bin/env python3
"""
Testfälle für das Kreuzwort-Riddle Framework

Diese Tests demonstrieren die LLM-freundliche API und automatische Validierung.
"""

from kreuzwortriddle import LLMKreuzwortAPI

def test_basic_validation():
    """Testet die grundlegende Validierungslogik"""
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
    try:
        result2 = api.add_question("", "Test", "horizontal")
    print(f"Test 1 - Ungültige Frage: {result2}")
    
    # Test 3: Problem mit Überschneidungen
    result3 = api.add_question(
            "Hauptstadt von Frankreich",
            "Paris",
            "vertical"
    )
    
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
    
    # Diese Tests zeigen die LLM-freundliche Fehlerbehandlung")
    
    # Test mit nicht-alphabetischen Zeichen
    try:
        result4 = api.add_question(
                "Frage mit Zahlen",
                "Test123",
                "horizontal"
    )
    
    print("\n=== FRAMEWORK TEST ABGESCHLOSSEN ===\n")