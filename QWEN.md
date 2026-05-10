# QWEN Framework Dokumentation - Kreuzwort-Riddle Framework

## Projektübersicht
Framework zur Erstellung von Kreuzworträtseln für LLMs

## LLM-spezifische Hinweise
- Framework automatisiert die Rätselerstellung
- LLM kümmert sich nur um Fragen/Antworten und deren Validierung
- Automatische Validierung und Fehlerbehebungs-Feedback

## Setup Status
- Git Repository initialisiert
- Core-Library funktional (Backtracking-Algorithmus, Parallel-Berührungsprüfung)
- BonusRevealSystem integriert (revealed_positions wird befüllt)
- BonusWordConstraints in Core-Library migriert
- Tests mit Assertions
- REST-API funktional
- MCP-Server stdio-basiert
- `llm_bonus_info.py` entfernt (nach `kreuzwortriddle.py` migriert)
- Siehe `PROJEKTANALYSE.md` für Details

## Framework-Anforderungen
Das Framework muss folgenden Anforderungen genügen:
1. **LLM-freundliche API**: Einfache Eingabe von Fragen und Antworten
2. **Automatische Validierung**: Prüfung auf widersprüchliche Kreuzungen
3. **Intelligentes Fehler-Feedback**: Präzise Hinweise für Korrekturen
4. **Resilienz bei unmöglichen Rätseln**: Identifikation "fauler" Fragen
