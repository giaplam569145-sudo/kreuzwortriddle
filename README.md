# Crossword Riddle Framework

A Python framework for automatically creating crossword puzzles, specially developed for LLMs.

## Overview

The Crossword Riddle Framework automates the technical complexity of puzzle creation, allowing LLMs to focus on what they do best: creating questions and answers.

### Main Features

- **LLM-Friendly API**: Simple input of questions and answers.
- **Automatic Validation**: Checks for conflicting intersections.
- **Intelligent Error Feedback**: Precise hints for corrections.
- **Resilience for Impossible Puzzles**: Identification of "lazy" questions.
- **Bonus Word System**: Progressive revealing of additional words.
- **REST API**: Remote access for external systems.
- **MCP Server**: Integration into MCP-enabled development environments.

## Installation

```bash
# Clone the repository
git clone <repository-url>
cd crossword-riddle

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

### Basic Usage

```python
from kreuzwortriddle import LLMKreuzwortAPI

# Create an API instance
api = LLMKreuzwortAPI(width=15, height=15)

# Add questions
api.add_question("Capital of Germany", "Berlin", "horizontal")
api.add_question("Capital of France", "Paris", "vertical")

# Validate
validation = api.validate_all()
print(validation)

# Generate puzzle
generation = api.generate()
print(generation)

# Display grid
if generation["status"] == "success":
    grid = api.get_grid()
    for row in grid:
        print(' '.join(cell if cell else '.' for cell in row))
```

### Bonus Word System

```python
# After successful generation
if generation["status"] == "success":
    api.set_bonus_word("EUROPA")

    # Progressively reveal letters
    while True:
        letter = api.reveal_next_bonus_letter()
        if not letter:
            break
        print(f"Revealed: {letter}")
        print(f"Status: {api.get_bonus_word_hint()}")
```

## API Reference

### LLMKreuzwortAPI

The main API class for interacting with the framework.

#### Methods

- `add_question(question, answer, orientation)`: Adds a new question.
- `validate_all()`: Validates all questions.
- `generate()`: Generates the puzzle.
- `get_problems()`: Identifies problematic questions.
- `get_grid()`: Returns the generated grid.
- `get_placements()`: Returns the word placements.
- `set_bonus_word(word)`: Sets the bonus word.
- `reveal_next_bonus_letter()`: Reveals the next letter of the bonus word.
- `get_bonus_word_hint()`: Returns the current hint for the bonus word.

## REST API

The server can be started with `python rest_api.py`:

### Endpoints

- `POST /api/questions`: Add a question.
- `GET /api/validate`: Validate all questions.
- `POST /api/generate`: Generate the puzzle.
- `GET /api/problems`: Identify problems.
- `POST /api/bonus`: Set the bonus word.
- `POST /api/bonus/reveal`: Reveal a bonus letter.
- `GET /api/status`: Query the framework status.
- `POST /api/reset`: Reset the framework.

## MCP Server

The MCP server allows integration into MCP-enabled development environments:

```bash
python mcp_server.py
```

## Testing

To run the test suite, use the following command:

```bash
python test_framework.py
```

## Contributing

Contributions are welcome! Please see the `CONTRIBUTING.md` file for more information.

## License

MIT License - see the LICENSE file for details.
