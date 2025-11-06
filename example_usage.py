#!/usr/bin/env python3
"""
Beispiel-Nutzung des Kreuzwort-Riddle Frameworks für LLMs

Dieses Beispiel zeigt, wie LLMs das Framework nutzen können, um sich auf das Wesentliche zu konzentrieren: Fragen und Antworten.

Autor: Qwen Code (2025)
"""

from kreuzwortriddle import LLMKreuzwortAPI

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

# Frage 3
result3 = api.add_question(
    "Hauptstadt von Italien",
    "Rom",
    "horizontal"
)

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

# Diese Frage wird Probleme verursachen:
result4 = api.add_question(
    "Einzigartiges Wort ohne Überschneidungen:")

# "Faule" Frage - keine gemeinsamen Buchstaben
result5 = api.add_question(
    "Sehr spezifisches Wort",
    "Xylophon",
    "horizontal"
)

print("\n=== LLM-HINWEISE ===\n")
print("LLM: Wenn du Fehlermeldungen siehst wie:")
print("'Antwort hat keine gemeinsamen Buchstaben mit anderen Antworten")

# Finale Validierung
final_validation = api.validate_all()
print(f"Finale Validierung: {final_validation}")

print("\n=== WICHTIGE FEHLERMELDUNGEN ===\n")

# LLM-spezifische Fehlermeldungen
print("\nTypische Fehlermeldungen für LLMs:")
print("- 'Frage-Text ist leer' → Gib einen sinnvollen Fragetext ein")
print("- 'Antwort ist leer' → Gib eine gültige Antwort ein")
print("- 'Antwort muss mindestens 2 Buchstaben lang sein")
print("- 'Antwort darf nur Buchstaben enthalten'")
print("- 'Antwort ist zu lang' → Kürze die Antwort")

print("\n=== FRAMEWORK ERFOLGREICH INITIALISIERT ===\n")