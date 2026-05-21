# AGENTS.md

## Project

Crossword puzzle framework designed for LLM consumption. Core library is a single file; everything else is optional integration layers. UI strings, comments, and docstrings are in German throughout.

## Architecture

- **`kreuzwortriddle.py`** — Core library. Public API class is `LLMKreuzwortAPI`. Also exports `Orientation`, `ValidationError`, `BonusRevealSystem`, `BonusWordConstraints`, `KreuzwortRiddle`.
- **`rest_api.py`** — Flask REST API wrapping `LLMKreuzwortAPI`. Session-based (thread-safe). Optional; requires `flask`.
- **`mcp_server.py`** — Stdio-based MCP server wrapping `LLMKreuzwortAPI`. Optional; requires `mcp`.
- **`test_framework.py`** — Pytest test suite (32 tests).
- **`example_usage.py`**, **`bonus_example.py`** — Example scripts.

## Running

```sh
python kreuzwortriddle.py          # Core self-test
pytest test_framework.py -v        # All tests (pytest)
python rest_api.py                 # Flask dev server on :5000
python -m ruff check .             # Lint
python -m mypy kreuzwortriddle.py  # Type check
```

No build step, no virtualenv required for core lib. Optional deps in `requirements.txt`.

## Known issues

- **Grid generation for large word sets**: Uses permutation fallback for ≤8 remaining words, random sampling (100 attempts) for >8. Very large sets may still fail.
- **Flask session-based state**: Uses signed cookies. For production, use a proper session backend.

## Conventions

- Linter: `ruff` (E, F, W, I rules). Type checker: `mypy`. Config in `pyproject.toml`.
- Answers are German words; validation enforces `.isalpha()` (no umlauts ß/ä/ö/ü — `.isalpha()` does accept them but the framework doesn't normalize them).
- All API methods return `Dict[str, Any]` with a `"status"` key (`"success"`, `"error"`, `"validation_errors"`, `"generation_failed"`, `"problems_found"`, `"no_problems"`).
- `ValidationError` is raised internally by `KreuzwortRiddle.add_question()` but caught and returned as a dict by `LLMKreuzwortAPI.add_question()`. LLM-facing code should use `LLMKreuzwortAPI`, not `KreuzwortRiddle` directly.
- **Language convention:**
  - Code identifiers (class names, method names, variables) → **English** (Python ecosystem standard)
  - Docstrings, comments, user-facing error/status messages → **German** (project domain convention)
