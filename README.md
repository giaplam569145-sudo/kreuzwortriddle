# Kreuzwort-Riddle Framework

A Python framework for automatically creating crossword puzzles, specially developed for LLMs.

## Overview

The Kreuzwort-Riddle Framework automates the technical complexity of puzzle creation, allowing LLMs to focus on what they do best: creating questions and answers.

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
cd kreuzwortriddle

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
from kreuzwortriddle import BonusRevealSystem

# Initialize the bonus word system
bonus_system = BonusRevealSystem()
bonus_system.set_bonus_word("EUROPA")

# After successful generation
if generation["status"] == "success":
    bonus_system.update_available_letters(api.get_grid())

    # Progressively reveal letters
    while bonus_system.can_reveal_bonus_letter():
        letter = bonus_system.reveal_next_letter()
        print(f"Revealed: {letter}")
        print(f"Status: {bonus_system.get_bonus_word_hint()}")
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

#### Return Formats

All methods return dictionaries with a consistent structure:

```python
{
    "status": "success|error|validation_errors|generation_failed",
    "message": "Description of the result",
    "data": {...}  # Optional, additional data
}
```

### BonusRevealSystem

Manages the progressive revealing of the bonus word.

#### Methods

- `set_bonus_word(word)`: Sets the bonus word.
- `update_available_letters(grid)`: Updates the available letters.
- `can_reveal_bonus_letter()`: Checks if a letter can be revealed.
- `reveal_next_letter()`: Reveals the next letter.
- `get_bonus_word_hint()`: Returns the current hint.

## REST API

The server can be started with `python rest_api.py`:

### Endpoints

- `POST /api/questions`: Add a question.
- `GET /api/validate`: Validate all questions.
- `POST /api/generate`: Generate the puzzle.
- `GET /api/problems`: Identify problems.
- `GET/POST /api/bonus`: Manage the bonus word.
- `POST /api/bonus/reveal`: Reveal a bonus letter.
- `GET /api/status`: Query the framework status.
- `POST /api/reset`: Reset the framework.

### Example Requests

```bash
# Add a question
curl -X POST http://localhost:5000/api/questions \
  -H "Content-Type: application/json" \
  -d '{"question": "Capital of Germany", "answer": "Berlin", "orientation": "horizontal"}'

# Generate the puzzle
curl -X POST http://localhost:5000/api/generate

# Set the bonus word
curl -X POST http://localhost:5000/api/bonus \
  -H "Content-Type: application/json" \
  -d '{"bonus_word": "EUROPA"}'
```

## MCP Server

The MCP server allows integration into MCP-enabled development environments:

```bash
python mcp_server.py
```

Available Tools:
- `add_question`: Add a question.
- `validate_all`: Validate questions.
- `generate_riddle`: Generate the puzzle.
- `get_problems`: Identify problems.
- `set_bonus_word`: Set the bonus word.
- `reveal_bonus_letter`: Reveal a bonus letter.
- `get_status`: Get the status.
- `reset_framework`: Reset the framework.

## Validation Rules

### Questions

- Question text must not be empty.
- The answer must be 2-20 letters long.
- The answer must only contain letters (no numbers or special characters).

### Puzzle Generation

- At least 2 questions are required.
- Questions must be able to intersect (common letters).
- Grid boundaries must be respected.

### Bonus Word

- 3-8 letters in length.
- All letters must be available in the grid.
- A maximum of one letter per word for the bonus word.

## Error Handling

The framework provides detailed error messages for LLMs:

### Common Errors

- `"Question text is empty"` → Enter a meaningful question text.
- `"Answer is empty"` → Enter a valid answer.
- `"Answer must be at least 2 letters long"` → Use a longer answer.
- `"Answer must only contain letters"` → Remove special characters.
- `"Answer has no common letters with other answers"` → Add a question with overlapping letters.

## Examples

### Complete Example

```python
from kreuzwortriddle import LLMKreuzwortAPI, BonusRevealSystem

# Initialize the framework
api = LLMKreuzwortAPI()
bonus_system = BonusRevealSystem()

# Add questions
questions = [
    ("Capital of Germany", "Berlin", "horizontal"),
    ("River in Germany", "Elbe", "vertical"),
    ("State", "Bayern", "horizontal"),
    ("Mountains", "Alpen", "vertical")
]

for question, answer, orientation in questions:
    result = api.add_question(question, answer, orientation)
    print(f"Added question: {result}")

# Validate and generate
validation = api.validate_all()
if validation["status"] == "valid":
    generation = api.generate()
    if generation["status"] == "success":
        # Bonus word system
        bonus_system.set_bonus_word("DEUTSCH")
        bonus_system.update_available_letters(api.get_grid())

        # Display grid
        grid = api.get_grid()
        for row in grid:
            print(' '.join(cell if cell else '.' for cell in row))
```

## Testing

```bash
# Framework tests
python test_framework.py

# Example usage
python example_usage.py

# Bonus word examples
python bonus_example.py
```

## Architecture

The framework consists of several layers:

1.  **Core Layer**: `KreuzwortRiddle` - Main logic.
2.  **API Layer**: `LLMKreuzwortAPI` - LLM-friendly interface.
3.  **Bonus Layer**: `BonusRevealSystem` - Bonus word logic.
4.  **Service Layer**: REST API and MCP server.
5.  **Utility Layer**: Helper functions and validation.

## Contributing

1.  Create a fork.
2.  Create a feature branch.
3.  Implement changes.
4.  Run tests.
5.  Create a pull request.

## License

MIT License - see the LICENSE file for details.

## Author

Qwen Code (2025)
