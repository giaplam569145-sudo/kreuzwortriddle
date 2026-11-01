# Anforderungsanalyse & Feature-Vorschläge: Kreuzwort-Riddle Framework

**Datum:** Mai 2026
**Autor:** Jules (Software Engineer)
**Projekt:** Kreuzwort-Riddle Framework für LLMs

---

## 1. Einleitung & Ist-Zustands-Analyse

Das **Kreuzwort-Riddle Framework** ist eine spezialisierte Python-Bibliothek, die Large Language Models (LLMs) dabei unterstützt, zweidimensionale Kreuzworträtsel verlässlich zu generieren. LLMs sind stark in Weltwissen, Wortassoziationen und kreativem Fragenschreiben, haben jedoch grundlegende Defizite bei strikten geometrischen, räumlichen und kombinatorischen Randbedingungen (Schnittpunkte, Längen, Parallelitätsverbote).

### 1.1 Aktuelle Architektur
- **Core Library (`kreuzwortriddle.py`, `models.py`)**: Kapselt Datenmodelle (`Question`, `WordPlacement`, `Orientation`), Basisprüfungen und die High-Level-Fassade `LLMKreuzwortAPI`.
- **Gittergenerierung (`grid_generator.py`)**: Rekursives Backtracking zur Wortplatzierung mit Wortlängen-Sortierung.
- **Bonuswort-System (`bonus_system.py`)**: Progressives Aufdecken eines Lösungswortes basierend auf den im Gitter vorhandenen Buchstaben.
- **Modulares Regelsystem (`gamemode.py`, `modes.py`)**: Basisklasse `GameMode` zur Modifikation der Rätsellogik (`ThemeBasedRiddle`, `NumberRiddle`, `ReverseRiddle`).
- **Schnittstellen (`rest_api.py`, `mcp_server.py`)**: Session-basierte Flask REST-API sowie stdio-basierter MCP-Server mit 8 Tools für KI-Agenten und Entwicklungsumgebungen.
- **Test-Suite (`test_framework.py`)**: 49 automatisierte Pytest-Tests für Validierung, Gittererstellung und Bonuswortlogik.

### 1.2 Identifizierte Lücken & Erweiterungspotenziale
Aus der Analyse des Codes und dem Abgleich mit typischen Anforderungen moderner Rätsel-Engines und LLM-Workflows ergeben sich folgende Optimierungsfelder:
1. **Algorithmen & Skalierung**: Backtracking arbeitet aktuell zellen-orientiert ohne Constraint-Satisfaction-Heuristiken (AC-3 / MRV) oder flexible Wortausrichtung (nur fixierte horizontale/vertikale Vorgabe je Frage).
2. **Deutsche Sprachspezifika**: Fehlende Normalisierung von Umlauten (Ä, Ö, Ü) und ß sowie automatische Anpassung von Rätsel-Konventionen (z. B. `AE`, `OE`, `UE`, `SS`).
3. **Export- und Ausgabevielfalt**: Bisher existiert nur Rohdaten-Ausgabe (Matrix & Placements). Formate wie IPUZ (Industriestandard), druckfertiges SVG/PDF oder interaktives HTML fehlen.
4. **LLM-Kollaboration & Wortempfehlungen**: LLMs müssen Wörter raten; eine API für Schnittstellen-Patterns (z. B. "Finde Wort mit `_E_L__`") existiert noch nicht.
5. **Session- & Speicher-Persistenz**: Flask nutzt cookie-basierte Serialisierung; eine saubere Persistenzschicht (SQLite/JSON-Storage) fehlt.
6. **Interaktive Lösungsprüfung & Hint-System**: Keine Möglichkeit für Clients, Antworten feldweise zu prüfen oder schrittweise Hilfestellungen zu geben.
7. **Symmetrische & professionelle Gittermasken**: Für Zeitungsrätsel (z. B. Schwedenrätsel oder klassische Kreuzgitter mit Blocksperren) fehlen strukturierte Masken.

---

## 2. Ausgewählte Feature-Vorschläge (Übersicht)

| Nr. | Feature | Kategorie | Priorität | Komplexität |
|---|---|---|---|---|
| **1** | Automatische deutsche Sprach- & Umlaut-Normalisierung | Core / Sprachverarbeitung | Hoch | Gering (1–2 Tage) |
| **2** | Dynamische Orientierungsauflösung & Constraint-Backtracking | Algorithmus / Grid | Hoch | Mittel (3–4 Tage) |
| **3** | Wortvorschlags-Engine für LLMs (Pattern-Matching / RegEx-Suche) | LLM-Support / API | Hoch | Mittel (2–3 Tage) |
| **4** | Multiformat-Export (IPUZ-Standard, SVG-Grafik & HTML/CSS) | Export / Interoperabilität | Mittel | Mittel (3–4 Tage) |
| **5** | Interaktive Validierungs- & Hint-API für Rätsellöser | Gameplay / REST & MCP | Mittel | Gering (2 Tage) |
| **6** | Persistenz-Schicht (Pluggable Storage / SQLite & JSON) | Architektur / Backend | Mittel | Mittel (2–3 Tage) |
| **7** | Vordefinierte Gitter-Layouts & Schwedenrätsel-Modus | GameModes / Layout | Niedrig | Hoch (4–5 Tage) |

---

## 3. Detaillierte Feature-Beschreibungen

### Feature 1: Automatische deutsche Sprach- & Umlaut-Normalisierung
- **Ziel / Motivation:**
  Im Deutschen sind Umlaute (Ä, Ö, Ü) und das scharfe S (ß) in Kreuzworträtseln üblich. Aktuell erlaubt `models.py` zwar `.isalpha()`, behandelt aber Umlaute und ß uneinheitlich bzw. untersagt sie in strikten Konventionen. In klassischen Kreuzworträtseln werden Umlaute meist durch Doppelvokale (`AE`, `OE`, `UE`) und `ß` durch `SS` ersetzt oder wahlweise als Einzelbuchstaben behandelt.
- **Funktionale Anforderungen:**
  - Konfigurierbarer Normalisierungsmodus: `UMLAUT_EXPAND` (Ä → AE, ß → SS), `UMLAUT_KEEP` (Ä bleibt Ä als Großbuchstabe) oder `STRIP_ACCENTS`.
  - Automatische Bereinigung und Konvertierung vor der Validierung und vor der Platzierung im Gitter.
  - Optionale Anzeige des transformierten Wortes im API-Ergebnis, damit LLMs transparent wissen, mit wie vielen Feldern gerechnet wird.
- **Architektur & Implementierung:**
  - Erweiterung von `Question` in `models.py` um eine Konfigurationsoption `umlaut_mode`.
  - Ergänzung einer Utility-Funktion `normalize_german_word(word: str, mode: str) -> str`.
  - Entsprechende Parameter in `LLMKreuzwortAPI`, `rest_api.py` und im MCP-Server-Tool `add_question`.
- **Mehrwert:**
  Beseitigt eine der häufigsten Fehlerquellen bei deutschsprachigen Rätsel-Inhalten und verhindert Gitterkollisionen durch unerwartete Wortlängen.

---

### Feature 2: Dynamische Orientierungsauflösung & Constraint-Backtracking
- **Ziel / Motivation:**
  Aktuell muss der Aufrufer (z. B. das LLM) für jedes Wort explizit `orientation="horizontal"` oder `"vertical"` angeben. Wenn zwei Wörter geometrisch nur andersherum kreuzen könnten, scheitert die Generierung, obwohl eine gültige Anordnung existiert. Zudem führt das schlichte Listen-Backtracking bei mehr als 6–8 Wörtern zu unnötigen Fehlversuchen.
- **Funktionale Anforderungen:**
  - Einführung eines neuen Enum-Wertes: `Orientation.AUTO`.
  - Bei `Orientation.AUTO` probiert der `GridGenerator` sowohl horizontale als auch vertikale Platzierungen aus.
  - Integration von Most Constrained Variable (MRV) und Least Constraining Value (LCV) Heuristiken zur Optimierung des Backtracking-Suchbaums.
  - Begrenzung der Suchtiefe / Timeout-Schutz gegen Deadlocks bei großen Wortmengen.
- **Architektur & Implementierung:**
  - Erweiterung des `Orientation`-Enums in `models.py` um `AUTO = "auto"`.
  - Anpassung der Backtracking-Schleife in `grid_generator.py` (`_backtrack_generate`): Verzweigung nach Orientierung, falls `AUTO` gewählt wurde.
  - Sortierung der noch nicht platzierten Fragen nach der Anzahl möglicher Schnittstellen mit bereits platzierten Wörtern.
- **Mehrwert:**
  Drastische Erhöhung der Erfolgsquote bei der automatischen Gittererstellung von aktuell ca. 70–80 % auf über 95 %, selbst bei größeren Fragensätzen (>10 Wörter).

---

### Feature 3: Wortvorschlags-Engine für LLMs (Pattern-Matching / Schnittstellen-Suche)
- **Ziel / Motivation:**
  Wenn ein LLM ein Kreuzworträtsel generiert und nach dem Platzieren von 3 Wörtern ein passendes Kreuzungswort sucht, "halluziniert" es oft Wörter, deren Buchstaben nicht zu den bereits existierenden Gitterzellen passen.
- **Funktionale Anforderungen:**
  - Neuer API-Endpunkt / MCP-Tool: `suggest_intersection_patterns()` bzw. `get_open_slots()`.
  - Gibt dem LLM eine Liste offener Schnittpunkte im aktuellen Gitter mit Musterbeschreibungen zurück (z. B. Slot 4: vertikal, Länge 6, Buchstabe 2 ist 'E', Buchstabe 5 ist 'L' -> Muster `.?E..L.?`).
  - Optionales eingebautes deutsches Basiswörterbuch (bzw. Wortlisten-Filter), um direkt konkrete Wortkandidaten vorzuschlagen.
- **Architektur & Implementierung:**
  - Neue Hilfsklasse `SlotAnalyzer` oder Methode `LLMKreuzwortAPI.get_open_intersection_slots()`.
  - Neuer REST-Endpunkt `GET /api/slots/suggest` und neues MCP-Tool `get_intersection_slots`.
- **Mehrwert:**
  Macht das Framework zu einem echten interaktiven Co-Piloten für LLM-Agenten. Das LLM muss nicht blind Wörter erraten, sondern kann gezielt passende Fragen für reale Gitterlücken formulieren.

---

### Feature 4: Multiformat-Export (IPUZ-Standard, SVG-Grafik & HTML/CSS)
- **Ziel / Motivation:**
  Aktuell liefert das Framework lediglich eine Text-Matrix (`List[List[str]]`) und Positionskoordinaten. Externe Anwendungen (Web-Apps, E-Paper, Druckvorlagen) müssen das Rendering komplett selbst implementieren.
- **Funktionale Anforderungen:**
  - **IPUZ-Export:** Generierung des offenen Standards für Kreuzworträtsel (`.ipuz` als JSON), kompatibel mit gängigen Rätsel-Apps.
  - **SVG-Renderer:** Generierung einer vektorbasierten SVG-Grafik des Rätselgitters mit Ziffernmarkierungen, Gitternetzlinien und abgetrennten Sperrfeldern (sowohl als leeres Rätsel als auch als Lösungsblatt).
  - **HTML/CSS-Export:** Druckfertiges oder responsives interaktives HTML-Template.
- **Architektur & Implementierung:**
  - Neues Modul `exporters.py` mit Klassen `IPUZExporter`, `SVGExporter` und `HTMLExporter`.
  - Ergänzung der Fassade: `api.export(format="ipuz"|"svg"|"html", solution=False)`.
  - Neuer REST-Endpunkt `GET /api/export?format=svg&solution=true`.
- **Mehrwert:**
  Sofortige visuelle Verwendbarkeit in Web-Frontends, Druckpublikationen und Standard-Rätsel-Software ohne zusätzliche Frontend-Entwicklung.

---

### Feature 5: Interaktive Validierungs- & Hint-API für Rätsellöser
- **Ziel / Motivation:**
  Bisher ist das Framework primär ein *Generator*. Oft soll ein generiertes Rätsel aber auch gespielt werden (z. B. in einer Web-App, im Chatbot oder in einem Lernspiel). Hierfür fehlen Endpunkte zur Lösungsüberprüfung und schrittweisen Hilfestellung.
- **Funktionale Anforderungen:**
  - Überprüfung einer Spielerantwort: `check_answer(question_number: int, user_answer: str) -> Dict`.
  - Gitterprüfung: `check_cell(x: int, y: int, letter: str) -> bool`.
  - Hinweis-System (Hints):
    - Aufdecken eines einzelnen Buchstabens an Position `(x, y)` oder für Frage `N`.
    - Aufdecken des ersten falschen Buchstabens.
    - Abfrage des aktuellen Fortschritts (z. B. "7 von 10 Wörtern korrekt gelöst, 85 % der Zellen gefüllt").
- **Architektur & Implementierung:**
  - Neue Klasse `CrosswordGameSession` oder Erweiterung von `LLMKreuzwortAPI`.
  - Endpunkte: `POST /api/game/check_answer`, `POST /api/game/hint`, `GET /api/game/progress`.
  - MCP-Tools für Agenten zur Begleitung menschlicher Spieler.
- **Mehrwert:**
  Wandelt die reine Generierungs-Bibliothek in eine vollwertige interaktive Gaming- und Rätsel-Engine um.

---

### Feature 6: Persistenz-Schicht (Pluggable Storage: JSON & SQLite)
- **Ziel / Motivation:**
  Aktuell speichert die REST-API die Sitzungsdaten ausschließlich in Flask-Session-Cookies (mittels Serialisierung), was unsicher ist, die Cookie-Größe bei großen Gittern sprengt und bei Serverneustarts verloren geht.
- **Funktionale Anforderungen:**
  - Abstraktes Storage-Interface (`BaseStorage`) mit Operationen `save_riddle(id, data)`, `load_riddle(id)`, `delete_riddle(id)`.
  - Implementierung zweier Backends:
    - `FileStorage`: Speichert Rätsel als versionierte `.json`-Dateien in einem Konfigurationsverzeichnis.
    - `SQLiteStorage`: Leichtgewichtige relationale Persistenz für Multi-User- oder Produktionsszenarien.
  - REST-API Endpunkte für Rätselverwaltung: `POST /api/riddles/save`, `GET /api/riddles/{id}`, `GET /api/riddles`.
- **Architektur & Implementierung:**
  - Neues Paket/Modul `storage.py`.
  - Saubere Trennung der Session-ID von der Datenhaltung (Session hält nur noch die `riddle_id`, nicht mehr das gesamte Python-Objekt).
- **Mehrwert:**
  Robuste Produktionsreife, Multi-User-Fähigkeit und Entlastung der HTTP-Header von Cookie-Payloads.

---

### Feature 7: Vordefinierte Gitter-Layouts & Schwedenrätsel-Modus
- **Ziel / Motivation:**
  Bisher generiert das Framework ausschließlich Freiform-Gitter ("Criss-Cross"), bei denen Wörter isoliert oder locker verbunden sind. Traditionelle Zeitungsrätsel und Schwedenrätsel erfordern jedoch dichte Gitter mit integrierten Hinweisfeldern (Pfeil- und Textfelder direkt im Gitter).
- **Funktionale Anforderungen:**
  - Neuer Spielmodus `SchwedenRiddle(GameMode)` in `modes.py`.
  - Unterstützung für Pfeil-Definitionen (Startfeld enthält Fragetext + Pfeilrichtung nach rechts oder unten).
  - Vorgefertigte Gittermasken (z. B. 9x9, 11x11, 15x15 mit symmetrischen Blindfeldern / Blocks).
  - Generator-Strategie zum Einpassen von Wörtern in eine fixe Maske.
- **Architektur & Implementierung:**
  - Erweiterung des `WordPlacement`-Modells um Clue-Koordinaten `(clue_x, clue_y)` und Pfeilrichtung.
  - Neuer Generator `MaskedGridGenerator` als spezialisierte Strategie.
- **Mehrwert:**
  Erfüllt den Wunsch nach authentischen Print- und Magazin-Kreuzworträtseln im klassischen europäischen Stil.

---

## 4. Priorisierung & Roadmap-Empfehlung

Für die nächste Entwicklungsphase (Release v1.2 und v1.3) wird folgende Umsetzungsreihenfolge empfohlen:

1. **Sprint 1 (Quick Wins & Kernqualität):**
   - **Feature 1 (Umlaut-Normalisierung):** Beseitigt unmittelbar bestehende UX- und Validierungs-Stolpersteine im deutschen Sprachraum.
   - **Feature 2 (Dynamische Orientierung `AUTO`):** Verbessert die Erfolgsquote des Backtracking-Generators massiv.

2. **Sprint 2 (LLM-Empowerment & Interoperabilität):**
   - **Feature 3 (Wortvorschlags-Engine / Slot-Analyzer):** Schließt die Lücke in der LLM-Interaktionsschleife.
   - **Feature 4 (IPUZ- & SVG-Export):** Schafft sofortigen visuellen und standardisierten Mehrwert für Endnutzer und Webclients.

3. **Sprint 3 (Enterprise & Gaming-Erweiterung):**
   - **Feature 5 (Interaktives Lösen / Hint-API)**
   - **Feature 6 (Persistenz-Schicht mit SQLite/JSON)**
   - **Feature 7 (Schwedenrätsel & Masken-Layouts)**

---

## 5. Fazit

Mit diesen 7 gezielten Features entwickelt sich das Kreuzwort-Riddle Framework von einem reinen Prototyp-Generator zu einer vollwertigen, produktionsreifen Rätsel-Plattform. Insbesondere die Kombination aus **intelligenterer Backtracking-Geometrie (Feature 2)**, **LLM-Wortvorschlägen (Feature 3)** und **offenen Exportstandards wie IPUZ/SVG (Feature 4)** bietet einen überragenden Mehrwert für LLM-Agenten und menschliche Anwender gleichermaßen.
