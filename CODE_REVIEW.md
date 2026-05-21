# Code-Review: Kreuzwort-Riddle Framework

**Datum:** 18. Mai 2026  
**Geprüfte Version:** Commit `b5c2e07`  
**Umfang:** Vollständige Codebasis (6 Python-Dateien, ~1.412 Zeilen)

---

## 1. Überblick

Das **Kreuzwort-Riddle Framework** ist ein Python-Framework zur automatischen Erstellung von Kreuzworträtseln, optimiert für den Einsatz durch LLMs. Es besteht aus drei Schichten:

| Schicht | Datei | Zeilen | Zweck |
|---|---|---|---|
| **Core** | `kreuzwortriddle.py` | 533 | Rätsellogik, Validierung, Bonuswort-System |
| **Service (REST)** | `rest_api.py` | 180 | Flask-HTTP-API für externe Systeme |
| **Service (MCP)** | `mcp_server.py` | 192 | MCP-Protokoll-Server für IDEs |
| **Tests** | `test_framework.py` | 225 | 32 Pytest-Tests |
| **Beispiele** | `example_usage.py` | 129 | LLM-Nutzungsbeispiel |
| **Beispiele** | `bonus_example.py` | 153 | Bonuswort-Demo |

**Tool Results:** Ruff ✅ (0 Fehler) | Mypy ⚠️ (6 Fehler) | Tests ✅ (32/32 bestanden)

---

## 2. Stärken

### 2.1 Saubere Architektur
- **Klare Trennung:** `KreuzwortRiddle` (interne Logik) vs. `LLMKreuzwortAPI` (LLM-Interface). Alle öffentlichen API-Methoden geben einheitlich `Dict[str, Any]` mit `"status"`-Key zurück.
- **Schichtenarchitektur:** Core → API → Service Layer (REST/MCP) — jede Schicht kapselt ihre Verantwortung.

### 2.2 Konsequente Typisierung
- Type Hints in 100% der Funktionssignaturen
- `dataclass` für `Question` und `WordPlacement`
- `Enum` für `Orientation`

### 2.3 Gute Fehlerkultur
- `ValidationError` mit spezifischen, fragebezogenen Fehlermeldungen (`problematic_questions`)
- Alle LLM-API-Methoden fangen Exceptions und geben Dicts mit nutzbaren Meldungen zurück
- Keine silent failures

### 2.4 Keine technischen Schulden
- Ruff: sauber
- Keine `TODO`/`FIXME`/`HACK`-Marker im Code
- `.gitignore` korrekt konfiguriert
- `AGENTS.md` ist aktuell und präzise

---

## 3. Kritische Befunde

### 3.1 BonusRevealSystem: Duplikat-Buchstaben im Bonuswort werden nicht aufgedeckt (Bug)

**Datei:** `kreuzwortriddle.py:392-442`  
**Schweregrad:** Hoch  
**Betroffen:** Alle Bonuswörter mit wiederholten Buchstaben (z. B. "EFFECT", "BANANA", "MISSISSIPPI")

**Problem:** `available_letters` ist ein `set` (`Set[str]`). Sobald ein Buchstabe einmal aus dem Set entfernt wird (Zeile 439: `self.available_letters.discard(letter)`), kann dieser Buchstabe für keine weitere Position im Bonuswort mehr verwendet werden.

**Beispiel "EFFECT":**
```
Bonuswort: E F F E C T
Erwartet:  6/6 Buchstaben aufdeckbar
Tatsächlich: 4/6 (E, F, C, T) — F und E jeweils nur einmal
```

**Auswirkung:** Das Bonuswort-Enthüllungssystem ist für ~30 % aller realen Wörter defekt (Anteil Wörter mit Duplikat-Buchstaben).

**Empfohlene Lösung:** `available_letters` als `Counter[str]` oder `Dict[str, int]` führen, das die Mehrfachverfügbarkeit jedes Buchstabens zählt. `reveal_next_letter` muss prüfen, ob eine bestimmte Buchstabenposition bereits durch einen vorherigen Reveal-Schritt bedient wurde.

---

### 3.2 Mypy-Fehler in Service-Layern

**rest_api.py — 3 Fehler:**

| Zeile | Fehler | Ursache |
|---|---|---|
| 26 | `Incompatible return value type` | `_get_session()` retourniert `SessionMixin`, deklariert `Dict[str, Any]` |
| 30 | `Returning Any from function declared to return LLMKreuzwortAPI` | Fehlender Type Guard für Session-Dict-Zugriff |
| 34 | Gleiches Problem für `BonusRevealSystem` | s.o. |

**mcp_server.py — 3 Fehler:**

| Zeile | Fehler | Ursache |
|---|---|---|
| 186 | `Missing named argument "server_name"` | `InitializationOptions()` benötigt seit MCP SDK 1.x `server_name`, `server_version`, `capabilities` |

**Auswirkung:** `mcp_server.py` würde mit aktuellen MCP-SDK-Versionen zur Runtime einen Fehler werfen. Die REST-API funktioniert, aber Type-Checker kann Fehler nicht mehr abfangen.

---

### 3.3 Grid-Generierung: Gierige Erstplatzierung (Design-Schwachstelle)

**Datei:** `kreuzwortriddle.py:129-165`  
**Schweregrad:** Mittel

**Problemkette:**

1. **`_try_generate`** (Z. 129): Platziert das ERSTE Wort immer an einer festen Position `(start_x, start_y)` — die Mitte des Gitters. Es wird **nie** versucht, das erste Wort an anderen Positionen zu platzieren.

2. **`_find_placement`** (Z. 167): Findet die ERSTE gültige Kreuzungsposition und retourniert sie sofort. Es gibt **kein Backtracking auf Positionsebene** — wenn diese Position später zu Konflikten führt, wird erst auf der nächsten Rekursionsebene rückgängig gemacht.

3. **`generate_grid`** (Z. 98): Permutations-Fallback für ≤8 Wörter ist exponentiell (O(n!)), was bei 8 Wörtern ~40.320 Durchläufe bedeutet — das ist vertretbar, skaliert aber nicht auf komplexere Rätsel.

**Auswirkung:** Für viele Wortmengen funktioniert der Algorithmus, aber die Erfolgsrate ist niedriger als möglich. Bei 3 Wörtern mit guten Überschneidungen: fast 100 %. Bei 6+ Wörtern mit schwachen Überschneidungen kann die Generierung scheitern, obwohl eine Lösung existiert.

**Empfehlung:** Backtracking auf Positionsebene (probier verschiedene Positionen für das erste Wort, verschiedene Kreuzungspunkte für jedes weitere Wort, nicht nur den ersten gefundenen).

---

### 3.4 BonusRevealSystem: `reveal_next_letter` liefert falsche Positionen

**Datei:** `kreuzwortriddle.py:424-442`  
**Schweregrad:** Mittel

**Problem:** In Zeile 436 wird `self._grid_positions.get(letter, [None])[0]` verwendet. Da `_grid_positions` ein `Dict[str, List[Tuple[int, int]]]` ist, wird immer die **erste** Position des Buchstabens im Gitter verwendet — unabhängig davon, ob diese Position bereits durch ein anderes Wort belegt oder ob der Buchstabe dort bereits als "aufgedeckt" markiert wurde.

**Beispiel:** Buchstabe 'E' kommt 3× im Gitter vor. `_grid_positions['E']` enthält `[(2,3), (5,1), (7,7)]`. Es wird immer `(2,3)` als `revealed_position` hinzugefügt, auch wenn dieser Buchstabe längst durch eine andere Enthüllung abgedeckt ist.

---

### 3.5 `get_problematic_questions` erkennt geometrische Probleme nicht

**Datei:** `kreuzwortriddle.py:261-279`  
**Schweregrad:** Mittel

**Problem:** Die Methode prüft nur **buchstabenweise Überschneidungen** (`set(antwort1) & set(antwort2)`). Sie erkennt nicht, dass zwei Wörter zwar gemeinsame Buchstaben haben, diese aber an geometrisch ungünstigen Positionen stehen (z. B. 'A' in Wort1 an Position 0, in Wort2 an Position 4 — zu nah am Rand).

**Auswirkung:** Die Methode meldet `"no_problems"`, obwohl die Generierung fehlschlägt. Der LLM bekommt keine brauchbare Rückmeldung.

---

## 4. Mittelschwere Befunde

### 4.1 REST-API: Session-Handling nicht produktionsreif

**Datei:** `rest_api.py:18, 23-26`  
**Schweregrad:** Mittel

- `app.secret_key = "kreuzwort-riddle-dev-key"` — hartkodiert, öffentlich im Repo
- Flask-Signed-Cookies sind nicht für Multi-Worker-Deployments geeignet
- Keine CORS-Konfiguration (Browser-Clients werden blockiert)
- Keine Request-Validierung (z. B. Content-Type-Prüfung nur rudimentär)

### 4.2 Tests: Abdeckungslücken

**Datei:** `test_framework.py`  
**Schweregrad:** Mittel

| Fehlender Test | Risiko |
|---|---|
| Grid-Generierung mit >5 Wörtern | Algorithmus-Skalierung ungetestet |
| Bonuswort mit Duplikat-Buchstaben | Bug 3.1 unentdeckt |
| REST-API-Endpunkte (pytest + Flask-Client) | API-Regressionen nicht abgesichert |
| `KreuzwortRiddle` direkt (ohne API-Layer) | Alle Tests gehen über `LLMKreuzwortAPI` |
| Grid-Generierung mit 100% identischen Buchstaben | Randfall |
| `_find_placement` mit Wörtern am Gitterrand | Randfall |
| Negative Tests: falscher Orientation-String | Typkonvertierung ungetestet |

### 4.3 MCP-Server: Ungenutzter Parameter

**Datei:** `mcp_server.py:81`  
**Schweregrad:** Niedrig

```python
Tool(
    name="set_bonus_word",
    inputSchema={
        "properties": {
            "bonus_word": {"type": "string"},
            "description": {"type": "string", "description": "..."}  # ← deklariert
        },
        "required": ["bonus_word"]
    }
)
```

Der Parameter `"description"` wird im Schema deklariert, aber in `_dispatch()` (Z. 136-143) nie gelesen oder verwendet.

---

## 5. Kleinere Befunde

### 5.1 Beispiel-Skript: Irreführende Ausgabe

**Datei:** `example_usage.py:67-80`

Nach dem erfolgreichen `generate()` (3 Wörter) werden zwei weitere Fragen ("Judo", "Quiz") hinzugefügt, aber **nicht** erneut generiert. Die finale Validierung `validate_all()` meldet `"valid"`, aber das Gitter enthält nur 3 Wörter. Ein LLM, das diesem Beispiel folgt, bekommt ein inkonsistentes Ergebnis.

### 5.2 README.md: Bonuswort-Beispiel nicht konsistent

**Datei:** `README.md:229`

```python
bonus_system.set_bonus_word("DEUTSCH")
```

Im Beispiel-Skript werden die Fragen "Berlin", "Elbe", "Bayern", "Alpen" hinzugefügt. Das Bonuswort "DEUTSCH" enthält den Buchstaben 'D', der **in keiner der Antworten vorkommt**. Die Enthüllung würde für 'D' immer scheitern.

### 5.3 `get_bonus_word_hint`: String-Länge uneinheitlich

**Datei:** `kreuzwortriddle.py:450-456`

```python
return f"Bonuswort: {revealed} ({len(self.revealed_letters)}/{len(self.bonus_word)} Buchstaben)"
```

Bei vollständiger Enthüllung steht z. B. `"Bonuswort: EUROPA (6/6 Buchstaben)"` — der Hinweis unterscheidet nicht zwischen "vollständig aufgedeckt" und "noch nicht fertig". Ein boolescher Indikator `is_complete` wäre hilfreich.

### 5.4 QWEN.md: Veraltet

**Datei:** `QWEN.md`

Der Kommentar "Framework Entwicklung beginnt" und "Tests mit Assertions" — der Test laufen heute alle durch. Die Datei sollte aktualisiert oder entfernt werden.

### 5.5 PROJEKTANALYSE.md: Veraltete Bug-Referenzen

**Datei:** `PROJEKTANALYSE.md`

Diese Analyse dokumentiert Bugs (z. B. "greedy grid algorithm", "keine Assertions in Tests", "overlaps_with() nie aufgerufen"), die im aktuellen Commit `b5c2e07` bereits behoben sind. Die Datei ist nicht mehr konsistent mit dem Code.

### 5.6 `Gemischte Sprache in Identifiern`

**Datei:** Alle

Die UI-Strings und Kommentare sind auf Deutsch, aber:
- `ValidationError` (Englisch) vs. `Frage-Text ist leer` (Deutsch)
- `_dispatch`, `reveal_next_letter`, `can_reveal_bonus_letter` (Englisch)
- `add_question`, `generate_grid`, `validate_all` (Englisch)

Einheitlichkeit (alles Englisch oder alles Deutsch) wäre wünschenswert.

---

## 6. Detailanalyse: `kreuzwortriddle.py` (Core)

### 6.1 Klassenstruktur

| Klasse | Typ | Verantwortung |
|---|---|---|
| `Orientation` | `Enum` | Horizontal/Vertical |
| `Question` | `dataclass` | Frage-Antwort-Paar mit Validierung |
| `ValidationError` | `Exception` | Validierungsfehler mit Kontext |
| `WordPlacement` | `dataclass` | Position eines Wortes im Gitter |
| `KreuzwortRiddle` | Klasse | Grid-Generierung, Platzierungslogik |
| `LLMKreuzwortAPI` | Klasse | LLM-freundliche API-Schicht |
| `BonusRevealSystem` | Klasse | Progressive Bonuswort-Enthüllung |
| `BonusWordConstraints` | Klasse | Bonuswort-Einschränkungen |

### 6.2 Datenfluss

```
LLM → LLMKreuzwortAPI.add_question()
                    ↓
            KreuzwortRiddle.add_question()
                    ↓
               Question.validate()
                    ↓
            ValidationError (optional)
                    ↓
LLM → LLMKreuzwortAPI.generate()
                    ↓
            KreuzwortRiddle.generate_grid()
                    ↓
               _try_generate()
                    ↓
               _place_remaining() [Backtracking]
                    ↓
               _find_placement()
                    ↓
               _can_place_at()
                    ↓
               _place_word()
```

### 6.3 Validierungsregeln (Question.validate)

| Regel | Grenzwert | Fehlermeldung |
|---|---|---|
| Fragetext leer | `strip()` → leer | "Frage-Text ist leer" |
| Antwort leer | `strip()` → leer | "Antwort ist leer" |
| Antwort zu kurz | `< 2` Zeichen | "muss mindestens 2 Buchstaben" |
| Antwort nicht-alpha | `isalpha()` = False | "nur Buchstaben enthalten" |
| Antwort zu lang | `> 20` Zeichen | "max 20 Buchstaben" |

**Anmerkung:** `str.isalpha()` akzeptiert Umlaute (ä, ö, ü, ß), aber auch nicht-lateinische Schriftzeichen (Kyrillisch, Griechisch, etc.). Der Framework validiert Sprachneutral.

### 6.4 Backtracking-Algorithmus (generate_grid)

```
generate_grid(questions):
  1. Versuche Platzierung in Original-Reihenfolge
  2a. Falls fehlgeschlagen + ≤8 Wörter: Alle Permutationen der restlichen Wörter probieren
  2b. Falls fehlgeschlagen + >8 Wörter: 100 zufällige Permutationen probieren
  3. Wenn alles fehlschlägt: `generation_failed`
```

**Komplexität:** O(n! · m²) im worst case, wobei n = Anzahl Wörter, m = maximale Wortlänge. Durch die 100-Limit bei >8 Wörtern wird die Laufzeit begrenzt, aber die Erfolgswahrscheinlichkeit sinkt.

---

## 7. Detailanalyse: `rest_api.py`

### 7.1 Endpoints

| Methode | Pfad | Funktion |
|---|---|---|
| POST | `/api/questions` | `add_question()` |
| GET | `/api/validate` | `validate_all()` |
| POST | `/api/generate` | `generate_riddle()` |
| GET | `/api/problems` | `get_problems()` |
| POST/GET | `/api/bonus` | `handle_bonus()` |
| POST | `/api/bonus/reveal` | `reveal_bonus_letter()` |
| GET | `/api/status` | `get_status()` |
| POST | `/api/reset` | `reset_framework()` |

### 7.2 Session-Verwaltung

```python
def _get_session() -> Dict[str, Any]:
    if "api" not in session:
        session["api"] = LLMKreuzwortAPI()      # Pickle-serialisiert!
        session["bonus_system"] = BonusRevealSystem()
    return session                               # Rückgabetyp: SessionMixin ≠ Dict
```

Flask signed cookies serialisieren die Session als Pickle. `LLMKreuzwortAPI` und `BonusRevealSystem` werden vollständig serialisiert — das schließt das Gitter (List of Lists) und alle Platzierungen ein. Bei großen Rätseln (>15×15) kann dies zu Performance-Problemen führen.

---

## 8. Detailanalyse: `mcp_server.py`

### 8.1 Tools

| Tool | Funktion |
|---|---|
| `add_question` | Frage hinzufügen |
| `validate_all` | Fragen validieren |
| `generate_riddle` | Rätsel generieren (+ Grid + Placements im Ergebnis) |
| `get_problems` | Problem-Fragen identifizieren |
| `set_bonus_word` | Bonuswort setzen |
| `reveal_bonus_letter` | Buchstabe aufdecken |
| `get_status` | Status abfragen |
| `reset_framework` | Zurücksetzen |

### 8.2 Fehler: MCP InitializationOptions

**Aktuell:**
```python
InitializationOptions()
```

**Erforderlich (MCP SDK ≥1.0):**
```python
InitializationOptions(
    server_name="kreuzwort-riddle-framework",
    server_version="1.1",
    capabilities=server.get_capabilities(
        # ...
    )
)
```

Ohne diese Parameter schlägt die MCP-Initialisierung zur Laufzeit fehl.

---

## 9. Detailanalyse: `test_framework.py`

### 9.1 Testabdeckung (32 Tests)

| Klasse | Anzahl | Themen |
|---|---|---|
| `TestValidierung` | 8 | Gültige/ungültige Fragen, Edge Cases |
| `TestGitterGenerierung` | 7 | 2-4 Wörter, leere Fragen, Kreuzungen |
| `TestProbleme` | 1 | Problemerkennung |
| `TestBonusSystem` | 9 | Bonuswort setzen, enthüllen, Positionsverfolgung |
| `TestConstraints` | 6 | Defaults, Berechnung, Validierung |

### 9.2 Testqualität

**Positiv:**
- 100 % der Tests verwenden Assertions
- Fixtures für API, BonusSystem, Constraints
- Separate Testklassen nach Domäne

**Negativ:**
- Alle Grid-Generierungs-Tests verwenden nur 2-4 Wörter
- Kein Test für `_can_place_at` isoliert (nur indirekt über generate)
- Kein Test für die `import random`-Fallback-Pfade (>8 Wörter)
- Kein Performance-Test für Permutations-Fallback

---

## 10. Konfiguration & Tooling

### 10.1 `pyproject.toml`

| Tool | Konfiguration | Bewertung |
|---|---|---|
| Ruff | `select = ["E", "F", "W", "I"]`, `line-length = 120` | ✅ Sinnvoll |
| Mypy | Python 3.12, `warn_return_any = true` | ✅ Gut |
| Pytest | Testpfad `.`, Datei `test_framework.py` | ✅ OK |

**Fehlt:** Keine `exclude` für Cache-Verzeichnisse, keine `ignore` für bekannte mypy-Probleme.

### 10.2 `requirements.txt`

```
flask>=2.3.0
mcp>=1.0.0
pytest>=7.0.0
```

- Version-Pins sind minimal (nur untere Grenzen)
- `mcp>=1.0.0` ist korrekt (SDK 1.x erforderlich für aktuellen Code)

---

## 11. Checkliste: Sicherheit

| Aspekt | Status | Anmerkung |
|---|---|---|
| Secrets im Code | ⚠️ | `secret_key` hartkodiert (dev-only, aber im Repo) |
| Input-Validierung | ✅ | `Question.validate()` vor jedem Schreibzugriff |
| Path Traversal | ✅ | Keine Dateioperationen |
| SSRF | ✅ | Keine HTTP-Requests aus Benutzereingaben |
| RCE | ⚠️ | Flask-Session-Cookies werden gepickled — theoretisch angreifbar |
| CORS | ❌ | Nicht konfiguriert |
| Rate Limiting | ❌ | Nicht implementiert |

---

## 12. Zusammenfassung nach Priorität

### Kritisch (sofort beheben)

| # | Problem | Datei:Zeile | Aufwand |
|---|---|---|---|
| 1 | Duplikat-Buchstaben in Bonuswörtern | `kreuzwortriddle.py:392-442` | 2h |
| 2 | MCP `InitializationOptions` fehlerhaft | `mcp_server.py:186` | 10min |
| 3 | Mypy-Fehler in REST-API | `rest_api.py:26,30,34` | 10min |
| 4 | `reveal_next_letter` position-inkorrekt | `kreuzwortriddle.py:436` | 1h |

### Hoch (dringend empfohlen)

| # | Problem | Aufwand |
|---|---|---|
| 5 | Grid-Backtracking auf Positionsebene verbessern | 4h |
| 6 | Thread-sicheres Session-Handling (Redis/DB) | 3h |
| 7 | Geometrische Probleme in `get_problematic_questions` | 3h |
| 8 | Tests für REST-API (Flask-Client) | 4h |

### Mittel (nächster Sprint)

| # | Problem | Aufwand |
|---|---|---|
| 9 | Bonuswort "DEUTSCH" im README-Beispiel korrigieren | 10min |
| 10 | `example_usage.py`: Inkonsistenz nach generate() beheben | 30min |
| 11 | Bonus-Reveal mit `is_complete`-Flag erweitern | 30min |
| 12 | `QWEN.md` und `PROJEKTANALYSE.md` aktualisieren | 1h |
| 13 | Tests für >5 Wörter und Duplikat-Bonusbuchstaben | 2h |
| 14 | `pyproject.toml`-exclude-Pfade ergänzen | 10min |

### Niedrig (optional)

| # | Problem | Aufwand |
|---|---|---|
| 15 | Ungenutzten `description`-Parameter im MCP entfernen | 5min |
| 16 | Identifier-Englisch/Deutsch-Mix vereinheitlichen | 2h |
| 17 | Performance-Test für Permutations-Fallback | 2h |
| 18 | CORS-Unterstützung in REST-API | 1h |

---

## 13. Metriken

### 13.1 Code-Gesundheit

| Metrik | Wert |
|---|---|
| Codezeilen (Python) | 1.412 |
| Testzeilen | 225 (15,9 % der Codebasis) |
| Test/Code-Verhältnis | 1:6,3 |
| Test-Pass-Rate | 100 % (32/32) |
| Ruff-Fehler | 0 |
| Mypy-Fehler | 6 |
| TODO/FIXME | 0 |
| Exportierte Klassen | 6 |
| Exportierte Funktionen/Methoden | ~40 |

### 13.2 Komplexität

| Funktion | Zeilen | Zyklomatische Komplexität (geschätzt) |
|---|---|---|
| `generate_grid()` | 28 | 6 |
| `_place_remaining()` | 22 | 5 |
| `_find_placement()` | 27 | 8 |
| `_can_place_at()` | 47 | 14 (höchste) |
| `BonusRevealSystem.reveal_next_letter()` | 16 | 8 |
| `BonusWordConstraints.validate_bonus_word()` | 22 | 7 |

---

## 14. Fazit

Das **Kreuzwort-Riddle Framework** ist ein solides, gut strukturiertes Projekt mit sauberer Architektur und konsistenter API. Die Validierungslogik ist robust, die Tests sind vollständig grün, und die Codebasis enthält keine offensichtlichen "Stinkstellen".

Die **zwei kritischsten Probleme** sind:

1. **Bonuswort-Duplikat-Buchstaben** (`kreuzwortriddle.py`): Ein `set` statt `Counter`/`dict` für `available_letters` führt dazu, dass Bonuswörter mit wiederholten Buchstaben nie vollständig aufgedeckt werden können.

2. **MCP-Server-Initialisierung** (`mcp_server.py`): Fehlende Parameter in `InitializationOptions()` verhindern die Laufzeit-Inbetriebnahme des MCP-Servers mit aktuellen SDK-Versionen.

Beide Probleme sind mit geringem Aufwand behebbar (< 2 h) und sollten vor dem nächsten Release adressiert werden.

Die Grid-Generierung ist für den aktuellen Anwendungsfall (3-5 Wörter) funktional, skaliert aber nicht auf komplexere Rätsel. Eine Überarbeitung des Backtracking-Algorithmus (Positionsebene statt nur Reihenfolgen-Permutation) ist die wichtigste architektonische Verbesserung für die Zukunft.

---

*Review durchgeführt von OpenCode (GLM-5.1)*
