# Projektanalyse: Kreuzwort-Riddle Framework

**Datum:** 10. Mai 2026  
**Analysiert von:** OpenCode (GLM-5.1)

---

## 1. Implementierungsfortschritt

### Core-Library (`kreuzwortriddle.py`) — ca. 80% fertig

| Komponente | Status | Bemerkung |
|---|---|---|
| `Orientation`-Enum | Fertig | OK |
| `Question`-Dataclass + Validierung | Fertig | Validierung funktioniert korrekt |
| `ValidationError` | Fertig | OK |
| `WordPlacement` + `overlaps_with()` | Fertig | `overlaps_with()` hat korrekte Logik, wird aber **nie aufgerufen** |
| `KreuzwortRiddle.add_question()` | Fertig | Validierung + ValidationError funktioniert |
| `KreuzwortRiddle.validate_all_questions()` | Fertig | OK |
| `KreuzwortRiddle.generate_grid()` | **Fehlerhaft** | Siehe Abschnitt 3 |
| `KreuzwortRiddle.get_problematic_questions()` | Fertig | OK |
| `LLMKreuzwortAPI` (5 Methoden) | Fertig | Alle Methoden funktional |
| `BonusRevealSystem` | **Teilweise** | Logik vorhanden, aber reveal-Mechanismus funktioniert nicht zuverlässig |

### REST-API (`rest_api.py`) — ca. 90% fertig

- 8 Endpoints implementiert (`/api/questions`, `/api/validate`, `/api/generate`, `/api/problems`, `/api/bonus`, `/api/bonus/reveal`, `/api/status`, `/api/reset`)
- Fehlerbehandlung mit try/except vorhanden
- **Problem:** Globale `api`- und `bonus_system`-Instanz; `/api/reset` nutzt `global` — nicht thread-safe
- Fehlt: keine Tests, keine Auth, keine CORS-Konfiguration

### MCP-Server (`mcp_server.py`) — ca. 70% fertig

- Tool-Registrierung über MCP-SDK vorhanden
- Alle 8 Tools implementiert
- **Problem:** `run()`-Methode ist ein Hybrid aus MCP-Server und FastAPI-HTTP-Server — kein echtes MCP-Protokoll über stdio/SSE
- `KreuzwortRiddleMCPServer` ist funktional, aber kein produktionsreifer MCP-Server

### `llm_bonus_info.py` — ca. 40% fertig

- Dupliziert `BonusRevealSystem`-Logik aus `kreuzwortriddle.py`
- `LLMBonusInfo`-Klasse ist implementiert, wird aber von **keinem anderen Modul** importiert
- `BonusWordConstraints` bietet nützliche Validierung, aber keine Integration in den Core
- `get_bonus_word_guidelines()` gibt statische Dicts zurück — eigentlich Documentation, kein Code

### Test-Dateien — ca. 50% effektiv

- `test_framework.py`: Print-basiert, **keine Assertions**, **kein Test-Framework**
- Test 3 (Bonuswort) schlägt **immer fehl** (`can_reveal_bonus_letter()` gibt `False` zurück, weil `available_letters` leer ist)
- Test 4 (Gitter-Generierung) schlägt **oft fehl** (greedy Algorithmus + ungünstige Wortkombination)

### Beispiele & Docs — ca. 75% fertig

- `example_usage.py`, `bonus_example.py`: Funktionale Beispiele
- `README.md`: Umfangreich, aber enthält Behauptungen die nicht stimmen (z.B. "Mindestens 2 Fragen erforderlich" — Code prüft das nicht)
- `context.md`: Keine Doku, sondern ein **gesamter Chat-Verlauf** einer Qwen-Code-Session (1.500+ Zeilen)
- `QWEN.md`: Veraltet ("Framework Entwicklung beginnt")
- `variants.md`, `slogans.txt`: Brainstorming-Notizen, kein Code

---

## 2. Codequalität

### Positive Aspekte

- **Konsistente API-Convention:** Alle `LLMKreuzwortAPI`-Methoden geben `Dict[str, Any]` mit `"status"`-Key zurück
- **Type Hints** durchgehend vorhanden
- **Dataclasses** für Datenstrukturen verwendet
- **Gute Fehlerbehandlung:** `ValidationError` mit spezifischen Fehlermeldungen pro Frage
- **Trennung von internen Klassen (`KreuzwortRiddle`) und LLM-API (`LLMKreuzwortAPI`)**

### Negative Aspekte

| Problem | Datei:Zeile | Schwere |
|---|---|---|
| `import random` wird nie verwendet | `kreuzwortriddle.py:14` | Niedrig |
| Greedy Grid-Algorithmus — bricht nach erstem fehlgeschlagenen Kreuzungsversuch ab | `kreuzwortriddle.py:142-149` | **Hoch** |
| `overlaps_with()` existiert, wird aber nie aufgerufen | `kreuzwortriddle.py:65-78` | Mittel |
| Keine Gitter-Kollisionsprüfung bei parallelen Wörtern | `kreuzwortriddle.py:194-216` | **Hoch** |
| `_can_place_at` prüft nur Buchstabenkonflikte, nicht ob Wörter parallel laufen und sich berühren | `kreuzwortriddle.py:207-214` | **Hoch** |
| `BonusRevealSystem` hat `revealed_positions` das nie gefüllt wird | `kreuzwortriddle.py:349` | Mittel |
| `LLMBonusInfo` in `llm_bonus_info.py` dupliziert `BonusRevealSystem` vollständig | `llm_bonus_info.py` | Mittel |
| Tests haben keine Assertions — Erfolg/Fehlschlag wird nur visuell geprüft | `test_framework.py` | Mittel |
| MCP-Server `run()` mischt MCP-SDK mit FastAPI — kein echtes MCP | `mcp_server.py:221-242` | Mittel |
| REST-API nutzt globale Mutable State — nicht thread-safe | `rest_api.py:17-19,229-231` | Mittel |
| `context.md` ist ein Chat-Verlauf (1.500+ Zeilen), keine Dokumentation | `context.md` | Niedrig |
| `QWEN.md` ist veraltet | `QWEN.md` | Niedrig |
| `import json` wird nie verwendet | `kreuzwortriddle.py:10` | Niedrig |

---

## 3. Bekannte Bugs im Detail

### Bug 1: Greedy Grid-Generierung (kritisch)

**Ort:** `kreuzwortriddle.py:142-149`

```python
for question in self.questions[1:]:
    placed = False
    for existing_placement in self.placements:
        if self._try_place_word(question, existing_placement):
            placed = True
            break  # <-- bricht nach dem ERFOLGREICHEN placement ab (OK)
    if not placed:
        return False  # <-- gibt sofort auf (SCHLECHT)
```

**Problem:** Wenn ein Wort nicht mit dem *ersten* passenden already-placed Wort gekreuzt werden kann, wird nicht mit den restlichen platzierten Wörtern versucht. Es wird sofort `False` zurückgegeben und die gesamte Generierung scheitert.

**Auswirkung:** `python test_framework.py` Test 4 ("Berlin", "Elbe", "Bayern", "Alpen") scheitert reproduzierbar.

### Bug 2: Keine Parallel-Berührungsprüfung

**Ort:** `kreuzwortriddle.py:194-216` (`_can_place_at`)

Die Methode prüft nur, ob ein Buchstabe mit einem anderen kollidiert. Sie prüft **nicht**, ob zwei horizontale Wörter direkt nebeneinander laufen und sich berühren (was zu ungültigen Kreuzworträtseln führt). Ebenso fehlt die Prüfung, ob am Anfang oder Ende eines Wortes ein Buchstabe eines rechtwinkligen Wortes steht, der nicht zum Wort gehört.

### Bug 3: Bonuswort-Enthüllung funktioniert nicht im Test

**Ort:** `test_framework.py:83-105`

`bonus_system.available_letters` ist leer, weil `update_available_letters()` nie mit einem tatsächlichen Gitter aufgerufen wird (Test 3 generiert kein Gitter). Daher gibt `can_reveal_bonus_letter()` immer `False` zurück und alle Enthüllungen sind `None`.

### Bug 4: `revealed_positions` wird nie befüllt

**Ort:** `kreuzwortriddle.py:349`

`BonusRevealSystem.revealed_positions` wird in `__init__` als leere Liste initialisiert, aber in keiner Methode jemals gefüllt. Die Liste taucht in `get_bonus_letter_info()` im Rückgabewert auf, ist aber immer leer.

---

## 4. Architektur-Bewertung

```
kreuzwortriddle.py (Core)     ← funktional, aber Algorithmus fragil
├── LLMKreuzwortAPI           ← gute Abstraktion, stabil
├── BonusRevealSystem         ← Logik vorhanden, nicht vollständig integriert
├── rest_api.py               ← funktional, einfache Flask-App
├── mcp_server.py             ← Hybrid-Lösung, kein echtes MCP
├── llm_bonus_info.py         ← redundante Duplikation, wird nicht genutzt
├── test_framework.py         ← keine echten Tests (nur prints)
├── example_usage.py          ← OK
├── bonus_example.py          ← OK, zeigt Integration mit llm_bonus_info
└── README.md                 ← gut, enthält aber falsche Behauptungen
```

**Fazit:** Das Projekt hat eine gute Grundstruktur und die LLM-API-Schicht ist sauber designed. Der schwächste Punkt ist der **Grid-Generierungsalgorithmus**, der für alle nicht-trivialen Wortmengen scheitert.

---

## 5. Empfehlungen (priorisiert)

1. **Grid-Algorithmus überarbeiten:** Backtracking statt Greedy, oder mindestens alle bereits platzierten Wörter durchprobieren statt beim ersten aufzugeben
2. **`llm_bonus_info.py` entfernen oder integrieren:** Entweder `BonusRevealSystem` in der Core-Library erweitern, oder `llm_bonus_info.py` als alleinige Quelle nutzen. Aktuell gibt es zwei halbfertige Implementierungen.
3. **Echte Tests schreiben:** pytest mit Assertions, nicht print-basiert
4. **`context.md` bereinigen:** 1.500 Zeilen Chat-Verlauf gehören nicht ins Repo (oder in `.gitignore`)
5. **`QWEN.md` aktualisieren:** Status ist veraltet
6. **Unbenutzte Imports entfernen:** `random`, `json`
7. **MCP-Server korrekt implementieren:** Entweder stdio-basiertes MCP oder als reiner FastAPI-Server, aber nicht beides mischen
8. **`_can_place_at` erweitern:** Parallele Wort-Berührungen prüfen
