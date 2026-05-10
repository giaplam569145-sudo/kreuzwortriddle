# AGENTS.md

## Project

Crossword puzzle framework designed for LLM consumption. Core library is a single file; everything else is optional integration layers. UI strings, comments, and docstrings are in German throughout.

## Architecture

- **`kreuzwortriddle.py`** — Core library. Public API class is `LLMKreuzwortAPI`. Also exports `Orientation`, `ValidationError`, `BonusRevealSystem`, `BonusWordConstraints`, `KreuzwortRiddle`.
- **`rest_api.py`** — Flask REST API wrapping `LLMKreuzwortAPI`. Optional; requires `flask`.
- **`mcp_server.py`** — Stdio-based MCP server wrapping `LLMKreuzwortAPI`. Optional; requires `mcp`.
- **`test_framework.py`** — Print-based test script with assertions (no test framework).
- **`example_usage.py`**, **`bonus_example.py`** — Example scripts.

## Running

```sh
python kreuzwortriddle.py          # Core self-test
python test_framework.py           # All tests (print-based with assertions)
python rest_api.py                 # Flask dev server on :5000
```

No build step, no virtualenv required for core lib. Only `rest_api.py` and `mcp_server.py` need extra deps from `requirements.txt`.

## Known issues

- **Grid generation uses backtracking with permutation fallback** (up to 8 remaining words). For very large word sets (>8 words after the first), the permutation fallback is skipped and only the original order is tried with backtracking.
- **`rest_api.py` uses global mutable state** — not thread-safe. The `/api/reset` endpoint uses `global`. Fine for dev server, not for production.

## Conventions

- No linter, formatter, or type checker is configured. No CI.
- Answers are German words; validation enforces `.isalpha()` (no umlauts ß/ä/ö/ü — `.isalpha()` does accept them but the framework doesn't normalize them).
- All API methods return `Dict[str, Any]` with a `"status"` key (`"success"`, `"error"`, `"validation_errors"`, `"generation_failed"`, `"problems_found"`, `"no_problems"`).
- `ValidationError` is raised internally by `KreuzwortRiddle.add_question()` but caught and returned as a dict by `LLMKreuzwortAPI.add_question()`. LLM-facing code should use `LLMKreuzwortAPI`, not `KreuzwortRiddle` directly.
