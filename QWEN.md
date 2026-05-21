# QWEN Framework Dokumentation - Kreuzwort-Riddle Framework

## Projektuebersicht
Framework zur Erstellung von Kreuzwortraetseln fuer LLMs.

## LLM-spezifische Hinweise
- Framework automatisiert die Raetselerstellung
- LLM kuemmert sich nur um Fragen/Antworten und deren Validierung
- Automatische Validierung und Fehlerbehebungs-Feedback

## Setup Status (18. Mai 2026)
- Core-Library: Backtracking-Algorithmus mit Permutations-Fallback
- BonusRevealSystem: Counter-basiert (Duplikat-Buchstaben werden korrekt aufgedeckt)
- BonusWordConstraints in Core-Library integriert
- Tests: 32 Pytest-Tests, alle gruen
- REST-API: 8 Endpoints, CORS-unterstuetzung (optional via flask_cors)
- MCP-Server: stdio-basiert, 8 Tools, MCP SDK 1.x
- Dokumentation: CODE_REVIEW.md, review_demo.py
