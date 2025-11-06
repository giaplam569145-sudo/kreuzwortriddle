# Kreuzwort-Riddle Framework

Ein Python-Framework zur automatischen Erstellung von Kreuzworträtseln, speziell für LLMs entwickelt.

## Überblick

Das Framework automatisiert die Erstellung von Kreuzworträtseln, sodass LLMs sich nur um das Recherchieren und Zusammenstellen der Fragen und Antworten kümmern müssen.

## LLM-spezifische Features

### 1. Vereinfachte API
- `add_question(question, answer, orientation)`
- `validate_all()`
- `generate()`
- `get_problems()

### 2. Automatische Validierung
- Prüfung auf leere Fragen/Antworten
- Validierung der Antwortlänge (2-20 Buchstaben)
- Automatische Identifikation "fauler" Fragen
- Intelligente Fehlermeldungen für LLMs

### 3. Intelligente Fehleridentifikation

## Verwendung für LLMs

```python
from kreuzwortriddle import LLMKreuzwortAPI

# API initialisieren
api = LLMKreuzwortAPI()

# Fragen hinzufügen
result = api.add_question(
    "Hauptstadt von Deutschland",
    "Berlin",
    "horizontal"
)

# Validierung aller Fragen
validation = api.validate_all()

# Rätsel generieren
generation = api.generate()

# Bei Problemen
problems = api.get_problems()
```

## Beispiel

```python
api = LLMKreuzwortAPI()

# Erfolgreiche Frage
api.add_question(
    "Hauptstadt von Frankreich",
    "Paris",
    "vertical"
)
```