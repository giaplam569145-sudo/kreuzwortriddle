#!/usr/bin/env python3
"""REST-API for the Kreuzwort-Riddle Framework.

Allows LLMs to use the framework's functionalities without direct Python
access.

Author: Qwen Code (2025)
"""

from flask import Flask, request, jsonify
import json
from functools import wraps
from typing import Dict, Any

from kreuzwortriddle import LLMKreuzwortAPI

app = Flask(__name__)
api = LLMKreuzwortAPI()

def handle_exceptions(f):
    """Decorator to handle common exceptions in API endpoints."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception as e:
            return jsonify({"status": "error", "message": f"Internal error: {str(e)}"}), 500
    return decorated_function

@app.route('/api/questions', methods=['POST'])
@handle_exceptions
def add_question():
    """Adds a new question via the REST API."""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "No data found in request body"}), 400
    result = api.add_question(
        data.get('question', ''),
        data.get('answer', ''),
        data.get('orientation', 'horizontal')
    )
    return jsonify(result)

@app.route('/api/validate', methods=['GET'])
@handle_exceptions
def validate_all():
    """Validates all questions via the REST API."""
    return jsonify(api.validate_all())

@app.route('/api/generate', methods=['POST'])
@handle_exceptions
def generate_riddle():
    """Generates the crossword puzzle via the REST API."""
    generation = api.generate()
    if generation["status"] == "success":
        generation["grid"] = api.get_grid()
        generation["placements"] = api.get_placements()
    return jsonify(generation)

@app.route('/api/problems', methods=['GET'])
@handle_exceptions
def get_problems():
    """Identifies problematic questions via the REST API."""
    return jsonify(api.get_problems())

@app.route('/api/bonus', methods=['POST', 'GET'])
@handle_exceptions
def handle_bonus():
    """Handles bonus word functions via the REST API."""
    if request.method == 'POST':
        data = request.get_json()
        bonus_word = data.get('bonus_word', '')
        if not bonus_word:
            return jsonify({"status": "error", "message": "Bonus word is required"}), 400
        api.set_bonus_word(bonus_word)
        return jsonify({"status": "success", "message": f"Bonus word '{bonus_word}' set"})
    elif request.method == 'GET':
        return jsonify({"status": "success", "hint": api.get_bonus_word_hint()})

@app.route('/api/bonus/reveal', methods=['POST'])
@handle_exceptions
def reveal_bonus_letter():
    """Reveals the next letter of the bonus word."""
    letter = api.reveal_next_bonus_letter()
    if letter:
        return jsonify({"status": "success", "revealed_letter": letter, "hint": api.get_bonus_word_hint()})
    else:
        return jsonify({"status": "error", "message": "No more letters available to reveal"}), 400

@app.route('/api/status', methods=['GET'])
@handle_exceptions
def get_status():
    """Returns the current status of the framework."""
    return jsonify({
        "status": "running",
        "framework_version": "1.0",
        "questions_count": len(api.riddle.questions),
        "placements_count": len(api.riddle.placements),
        "bonus_word_set": bool(api.riddle.bonus_word)
    })

@app.route('/api/reset', methods=['POST'])
@handle_exceptions
def reset_framework():
    """Resets the framework."""
    global api
    api = LLMKreuzwortAPI()
    return jsonify({"status": "success", "message": "Framework reset successfully"})

@app.errorhandler(404)
def not_found(error):
    """Handles 404 Not Found errors."""
    return jsonify({"status": "error", "message": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handles 500 Internal Server Error errors."""
    return jsonify({"status": "error", "message": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
