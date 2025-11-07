#!/usr/bin/env python3
"""REST-API for the Kreuzwort-Riddle Framework.

Allows LLMs to use the framework's functionalities without direct Python
access.

Author: Qwen Code (2025)
"""

from flask import Flask, request, jsonify
import json
from typing import Dict, Any

# Importiere unser bestehendes Framework
from kreuzwortriddle import LLMKreuzwortAPI, BonusRevealSystem

app = Flask(__name__)
api = LLMKreuzwortAPI()
bonus_system = BonusRevealSystem()


@app.route('/api/questions', methods=['POST'])
def add_question():
    """Adds a new question via the REST API.

    Endpoint: POST /api/questions
    Body:
        {
            "question": "Question text",
            "answer": "Answer",
            "orientation": "horizontal|vertical"
        }

    Returns:
        JSON response with the status of the operation.
    """
    try:
        data = request.get_json()

        if not data:
            return jsonify({
                "status": "error",
                "message": "Keine Daten im Request-Body gefunden"
            }), 400

        result = api.add_question(
            data.get('question', ''),
            data.get('answer', ''),
            data.get('orientation', 'horizontal')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Interner Fehler: {str(e)}"
        }), 500


@app.route('/api/validate', methods=['GET'])
def validate_all():
    """Validates all questions via the REST API.

    Endpoint: GET /api/validate

    Returns:
        JSON response with the validation result.
    """
    try:
        validation = api.validate_all()
        return jsonify(validation)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Validierungsfehler: {str(e)}"
        }), 500


@app.route('/api/generate', methods=['POST'])
def generate_riddle():
    """Generates the crossword puzzle via the REST API.

    Endpoint: POST /api/generate

    Returns:
        JSON response with the generation result, including the grid and
        placements on success.
    """
    try:
        generation = api.generate()

        if generation["status"] == "success":
            # Füge Gitter und Platzierungen hinzu
            generation["grid"] = api.get_grid()
            generation["placements"] = api.get_placements()

            # Aktualisiere Bonuswort-System
            bonus_system.update_available_letters(api.get_grid())

        return jsonify(generation)

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Generierungsfehler: {str(e)}"
        }), 500


@app.route('/api/problems', methods=['GET'])
def get_problems():
    """Identifies problematic questions via the REST API.

    Endpoint: GET /api/problems

    Returns:
        JSON response with a list of problematic questions.
    """
    try:
        problems = api.get_problems()
        return jsonify(problems)
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Fehler bei der Problemanalyse: {str(e)}"
        }), 500


@app.route('/api/bonus', methods=['POST', 'GET'])
def handle_bonus():
    """Handles bonus word functions via the REST API.

    POST: Sets the bonus word.
    GET: Returns the bonus word status.

    Endpoint: POST /api/bonus
    Body:
        {
            "bonus_word": "EUROPA",
            "description": "Kontinent"
        }

    Endpoint: GET /api/bonus

    Returns:
        JSON response with the bonus word information.
    """
    try:
        if request.method == 'POST':
            data = request.get_json()
            bonus_word = data.get('bonus_word', '')

            if not bonus_word:
                return jsonify({
                    "status": "error",
                    "message": "Bonuswort ist erforderlich"
                }), 400

            bonus_system.set_bonus_word(bonus_word)
            return jsonify({
                "status": "success",
                "message": f"Bonuswort '{bonus_word}' gesetzt",
                "bonus_info": bonus_system.get_bonus_letter_info()
            })

        elif request.method == 'GET':
            return jsonify({
                "status": "success",
                "bonus_info": bonus_system.get_bonus_letter_info(),
                "hint": bonus_system.get_bonus_word_hint()
            })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Bonuswort-Fehler: {str(e)}"
        }), 500


@app.route('/api/bonus/reveal', methods=['POST'])
def reveal_bonus_letter():
    """Reveals the next letter of the bonus word.

    Endpoint: POST /api/bonus/reveal

    Returns:
        JSON response with the revealed letter and the current bonus word
        hint.
    """
    try:
        if not bonus_system.can_reveal_bonus_letter():
            return jsonify({
                "status": "error",
                "message": "Keine weiteren Buchstaben verfügbar"
            }), 400

        letter = bonus_system.reveal_next_letter()
        return jsonify({
            "status": "success",
            "revealed_letter": letter,
            "hint": bonus_system.get_bonus_word_hint(),
            "bonus_info": bonus_system.get_bonus_letter_info()
        })

    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Enthüllungsfehler: {str(e)}"
        }), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """Returns the current status of the framework.

    Endpoint: GET /api/status

    Returns:
        JSON response with the framework's status information.
    """
    try:
        return jsonify({
            "status": "running",
            "framework_version": "1.0",
            "features": [
                "llm_friendly_api",
                "automatic_validation",
                "bonus_word_reveal",
                "rest_api_interface"
            ],
            "questions_count": len(api.riddle.questions),
            "placements_count": len(api.riddle.placements),
            "bonus_word_set": bool(bonus_system.bonus_word)
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Status-Fehler: {str(e)}"
        }), 500


@app.route('/api/reset', methods=['POST'])
def reset_framework():
    """Resets the framework.

    Endpoint: POST /api/reset

    Returns:
        JSON response with a success message.
    """
    try:
        global api, bonus_system
        api = LLMKreuzwortAPI()
        bonus_system = BonusRevealSystem()

        return jsonify({
            "status": "success",
            "message": "Framework erfolgreich zurückgesetzt"
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Reset-Fehler: {str(e)}"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handles 404 Not Found errors.

    Args:
        error: The error object.

    Returns:
        JSON response with a 404 error message.
    """
    return jsonify({
        "status": "error",
        "message": "Endpoint nicht gefunden"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handles 500 Internal Server Error errors.

    Args:
        error: The error object.

    Returns:
        JSON response with a 500 error message.
    """
    return jsonify({
        "status": "error",
        "message": "Interner Serverfehler"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# BEISPIEL-NUTZUNG FÜR LLMs MIT REST-API
"""
Example for using the REST API:

1. Add a question:
POST /api/questions
{
    "question": "Hauptstadt von Deutschland",
    "answer": "Berlin",
    "orientation": "horizontal"
}

2. Validate:
GET /api/validate

3. Generate:
POST /api/generate

4. Set bonus word:
POST /api/bonus
{
    "bonus_word": "EUROPA",
    "description": "Kontinent"
}

5. Reveal bonus letter:
POST /api/bonus/reveal

6. Get status:
GET /api/status
"""
