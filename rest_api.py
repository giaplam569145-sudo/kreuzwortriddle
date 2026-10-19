#!/usr/bin/env python3
"""REST-API fuer das Kreuzwort-Riddle Framework.

Ermöglicht LLMs ohne direkten Python-Zugriff die Framework-Funktionalitaeten zu nutzen.
Thread-sicher durch Session-basierte Instanzen.

Author: Qwen Code (2025)
"""

import os
from functools import wraps
from typing import cast

from flask import Flask, jsonify, request, session

from kreuzwortriddle import BonusRevealSystem, LLMKreuzwortAPI

app = Flask(__name__)
app.secret_key = os.environ.get(
    "KREUZWORT_SECRET_KEY", "kreuzwort-riddle-dev-key"
)

try:
    from flask_cors import CORS
    CORS(app)
except ImportError:
    pass


def _ensure_session() -> None:
    """Stellt sicher, dass die Framework-Instanzen in der Session existieren."""
    if "api" not in session:
        session["api"] = LLMKreuzwortAPI()
        session["bonus_system"] = BonusRevealSystem()


def _api() -> LLMKreuzwortAPI:
    _ensure_session()
    return cast(LLMKreuzwortAPI, session["api"])


def _bonus() -> BonusRevealSystem:
    _ensure_session()
    return cast(BonusRevealSystem, session["bonus_system"])


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
    """POST /api/questions — Frage hinzufuegen"""
    data = request.get_json()
    if not data:
        return jsonify({"status": "error", "message": "Keine Daten im Request-Body gefunden"}), 400

    result = _api().add_question(
        data.get('question', ''),
        data.get('answer', ''),
        data.get('orientation', 'horizontal')
    )
    return jsonify(result)


@app.route('/api/validate', methods=['GET'])
@handle_exceptions
def validate_all():
    """GET /api/validate — Alle Fragen validieren"""
    return jsonify(_api().validate_all())


@app.route('/api/generate', methods=['POST'])
@handle_exceptions
def generate_riddle():
    """POST /api/generate — Raetsel generieren"""
    api = _api()
    bonus = _bonus()
    generation = api.generate()

    if generation["status"] == "success":
        generation["grid"] = api.get_grid()
        generation["placements"] = api.get_placements()
        bonus.update_available_letters(api.get_grid())

    return jsonify(generation)


@app.route('/api/problems', methods=['GET'])
@handle_exceptions
def get_problems():
    """GET /api/problems — Problematische Fragen identifizieren"""
    return jsonify(_api().get_problems())


@app.route('/api/bonus', methods=['POST', 'GET'])
@handle_exceptions
def handle_bonus():
    """POST/GET /api/bonus — Bonuswort setzen oder abfragen"""
    bonus = _bonus()
    if request.method == 'POST':
        data = request.get_json()
        bonus_word = data.get('bonus_word', '')
        if not bonus_word:
            return jsonify({"status": "error", "message": "Bonuswort ist erforderlich"}), 400
        bonus.set_bonus_word(bonus_word)
        return jsonify({
            "status": "success",
            "message": f"Bonuswort '{bonus_word}' gesetzt",
            "bonus_info": bonus.get_bonus_letter_info()
        })
    else:
        return jsonify({
            "status": "success",
            "bonus_info": bonus.get_bonus_letter_info(),
            "hint": bonus.get_bonus_word_hint()
        })


@app.route('/api/bonus/reveal', methods=['POST'])
@handle_exceptions
def reveal_bonus_letter():
    """POST /api/bonus/reveal — Naechsten Buchstaben aufdecken"""
    bonus = _bonus()
    if not bonus.can_reveal_bonus_letter():
        return jsonify({"status": "error", "message": "Keine weiteren Buchstaben verfuegbar"}), 400
    letter = bonus.reveal_next_letter()
    return jsonify({
        "status": "success",
        "revealed_letter": letter,
        "hint": bonus.get_bonus_word_hint(),
        "bonus_info": bonus.get_bonus_letter_info()
    })


@app.route('/api/status', methods=['GET'])
@handle_exceptions
def get_status():
    """GET /api/status — Framework-Status abfragen"""
    api = _api()
    bonus = _bonus()
    return jsonify({
        "status": "running",
        "framework_version": "1.1",
        "features": [
            "llm_friendly_api",
            "automatic_validation",
            "bonus_word_reveal",
            "rest_api_interface"
        ],
        "questions_count": len(api.riddle.questions),
        "placements_count": len(api.riddle.placements),
        "bonus_word_set": bool(bonus.bonus_word)
    })


@app.route('/api/reset', methods=['POST'])
@handle_exceptions
def reset_framework():
    """POST /api/reset — Framework zuruecksetzen"""
    session["api"] = LLMKreuzwortAPI()
    session["bonus_system"] = BonusRevealSystem()
    return jsonify({"status": "success", "message": "Framework erfolgreich zurueckgesetzt"})


@app.errorhandler(404)
def not_found(error):
    return jsonify({"status": "error", "message": "Endpoint nicht gefunden"}), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({"status": "error", "message": "Interner Serverfehler"}), 500


if __name__ == '__main__':
    if app.secret_key == "kreuzwort-riddle-dev-key":
        print("Warnung: Verwende den Standard-Secret-Key. "
              "Setze KREUZWORT_SECRET_KEY fuer Produktion.", file=__import__('sys').stderr)
    app.run(debug=True, host='0.0.0.0', port=5000)
