# Kreuzwort-Riddle Framework

Ein Python-Framework zur automatischen Erstellung von Kreuzworträtseln, speziell entwickelt für LLMs.

## Überblick

Das Kreuzwort-Riddle Framework automatisiert die technische Komplexität der Rätselerstellung, sodass sich LLMs auf das Wesentliche konzentrieren können: die Erstellung von Fragen und Antworten.

### Hauptmerkmale

- **LLM-freundliche API**: Einfache Eingabe von Fragen und Antworten
- **Automatische Validierung**: Prüfung auf widersprüchliche Kreuzungen
- **Intelligentes Fehler-Feedback**: Präzise Hinweise für Korrekturen
- **Resilienz bei unmöglichen Rätseln**: Identifikation "fauler" Fragen
- **Bonuswort-System**: Progressive Enthüllung zusätzlicher Wörter
- **REST-API**: Fernzugriff für externe Systeme
- **MCP-Server**: Integration in MCP-fähige Entwicklungsumgebungen

## Installation

```bash
# Klonen des Repositories
git clone <repository-url>
cd kreuzwortriddle

# Abhängigkeiten installieren
pip install -r requirements.txt
```

## Schnellstart

### Grundlegende Nutzung

```python
from kreuzwortriddle import LLMKreuzwortAPI

# API-Instanz erstellen
api = LLMKreuzwortAPI(width=15, height=15)

# Fragen hinzufügen
api.add_question("Hauptstadt von Deutschland", "Berlin", "horizontal")
api.add_question("Hauptstadt von Frankreich", "Paris", "vertical")

# Validieren
validation = api.validate_all()
print(validation)

# Rätsel generieren
generation = api.generate()
print(generation)

# Gitter anzeigen
if generation["status"] == "success":
    grid = api.get_grid()
    for row in grid:
        print(' '.join(cell if cell else '.' for cell in row))
```

### Bonuswort-System

```python
from kreuzwortriddle import BonusRevealSystem

# Bonuswort-System initialisieren
bonus_system = BonusRevealSystem()
bonus_system.set_bonus_word("EUROPA")

# Nach erfolgreicher Generierung
if generation["status"] == "success":
    bonus_system.update_available_letters(api.get_grid())
    
    # Buchstaben progressiv aufdecken
    while bonus_system.can_reveal_bonus_letter():
        letter = bonus_system.reveal_next_letter()
        print(f"Aufgedeckt: {letter}")
        print(f"Status: {bonus_system.get_bonus_word_hint()}")
```

## API-Referenz

### LLMKreuzwortAPI

Die Haupt-API-Klasse für die Interaktion mit dem Framework.

#### Methoden

- `add_question(question, answer, orientation)`: Fügt eine neue Frage hinzu
- `validate_all()`: Validiert alle Fragen
- `generate()`: Generiert das Rätsel
- `get_problems()`: Identifiziert problematische Fragen
- `get_grid()`: Gibt das generierte Gitter zurück
- `get_placements()`: Gibt Wortplatzierungen zurück

#### Rückgabeformate

Alle Methoden geben Dictionaries mit konsistenter Struktur zurück:

```python
{
    "status": "success|error|validation_errors|generation_failed",
    "message": "Beschreibung des Ergebnisses",
    "data": {...}  # Optional, zusätzliche Daten
}
```

### BonusRevealSystem

Verwaltet die progressive Enthüllung des Bonuswortes.

#### Methoden

- `set_bonus_word(word)`: Setzt das Bonuswort
- `update_available_letters(grid)`: Aktualisiert verfügbare Buchstaben
- `can_reveal_bonus_letter()`: Prüft ob ein Buchstabe aufgedeckt werden kann
- `reveal_next_letter()`: Deckt den nächsten Buchstaben auf
- `get_bonus_word_hint()`: Gibt aktuellen Hinweis zurück

## REST-API

Der Server kann mit `python rest_api.py` gestartet werden:

### Endpoints

- `POST /api/questions`: Frage hinzufügen
- `GET /api/validate`: Alle Fragen validieren
- `POST /api/generate`: Rätsel generieren
- `GET /api/problems`: Probleme identifizieren
- `GET/POST /api/bonus`: Bonuswort verwalten
- `POST /api/bonus/reveal`: Bonusbuchstabe aufdecken
- `GET /api/status`: Framework-Status abfragen
- `POST /api/reset`: Framework zurücksetzen

### Beispiel-Requests

```bash
# Frage hinzufügen
curl -X POST http://localhost:5000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Hauptstadt von Deutschland", "answer": "Berlin", "orientation": "horizontal"}'

# Rätsel generieren
curl -X POST http://localhost:5000/api/generate

# Bonuswort setzen
curl -X POST http://localhost:5000/api/bonus \
  -H "Content-Type: application/json" \
  -d '{"bonus_word": "EUROPA"}'
```

## MCP-Server

Der MCP-Server ermöglicht die Integration in MCP-fähige Entwicklungsumgebungen:

```bash
python mcp_server.py
```

Verfügbare Tools:
- `add_question`: Frage hinzufügen
- `validate_all`: Fragen validieren
- `generate_riddle`: Rätsel generieren
- `get_problems`: Probleme identifizieren
- `set_bonus_word`: Bonuswort setzen
- `reveal_bonus_letter`: Bonusbuchstabe aufdecken
- `get_status`: Status abfragen
- `reset_framework`: Framework zurücksetzen

## Validierungsregeln

### Fragen

- Frage-Text darf nicht leer sein
- Antwort muss 2-20 Buchstaben lang sein
- Antwort darf nur Buchstaben enthalten (keine Zahlen oder Sonderzeichen)

### Rätselgenerierung

- Mindestens 1 Frage erforderlich (aber 1+ empfohlen für echte Kreuzung)
- Fragen müssen sich kreuzen können (gemeinsame Buchstaben)
- Gittergrenzen müssen eingehalten werden

### Bonuswort

- 3-8 Buchstaben Länge
- Alle Buchstaben müssen im Gitter verfügbar sein
- Maximal ein Buchstabe pro Wort für das Bonuswort

## Fehlerbehandlung

Das Framework gibt detaillierte Fehlermeldungen für LLMs:

### Häufige Fehler

- `"Frage-Text ist leer"` → Sinnvollen Fragetext eingeben
- `"Antwort ist leer"` → Gültige Antwort eingeben
- `"Antwort muss mindestens 2 Buchstaben lang sein"` → Längere Antwort verwenden
- `"Antwort darf nur Buchstaben enthalten"` → Sonderzeichen entfernen
- `"Antwort hat keine gemeinsamen Buchstaben mit anderen Antworten"` → Frage mit überschneidenden Buchstaben hinzufügen

## Beispiele

### Vollständiges Beispiel

```python
from kreuzwortriddle import LLMKreuzwortAPI, BonusRevealSystem

# Framework initialisieren
api = LLMKreuzwortAPI()
bonus_system = BonusRevealSystem()

# Fragen hinzufügen
questions = [
    ("Hauptstadt von Deutschland", "Berlin", "horizontal"),
    ("Fluss in Deutschland", "Elbe", "vertical"),
    ("Bundesland", "Bayern", "horizontal"),
    ("Gebirge", "Alpen", "vertical")
]

for question, answer, orientation in questions:
    result = api.add_question(question, answer, orientation)
    print(f"Frage hinzugefügt: {result}")

# Validieren und generieren
validation = api.validate_all()
if validation["status"] == "valid":
    generation = api.generate()
    if generation["status"] == "success":
        # Bonuswort-System
        bonus_system.set_bonus_word("DEUTSCH")
        bonus_system.update_available_letters(api.get_grid())
        
        # Gitter anzeigen
        grid = api.get_grid()
        for row in grid:
            print(' '.join(cell if cell else '.' for cell in row))
```

## Testing

```bash
# Pytest-Tests (32 Tests)
pytest test_framework.py -v

# Beispiel-Nutzung
python example_usage.py

# Bonuswort-Beispiele
python bonus_example.py

# Lint & Type Check
python -m ruff check .
python -m mypy kreuzwortriddle.py
```

## Architektur

Das Framework besteht aus mehreren Schichten:

1. **Core Layer**: `KreuzwortRiddle` - Hauptlogik
2. **API Layer**: `LLMKreuzwortAPI` - LLM-freundliche Schnittstelle
3. **Bonus Layer**: `BonusRevealSystem` - Bonuswort-Logik
4. **Service Layer**: REST-API und MCP-Server
5. **Utility Layer**: Hilfsfunktionen und Validierung

## Contributing

1. Fork erstellen
2. Feature-Branch erstellen
3. Änderungen implementieren
4. Tests durchführen
5. Pull Request erstellen

## Lizenz

MIT License - siehe LICENSE Datei für Details.

## Autor

Qwen Code (2025)