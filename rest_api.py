#!/usr/bin/env python3
"""
REST-API für das Kreuzwort-Riddle Framework

Ermöglicht LLMs ohne direkten Python-Zugriff die Framework-Funktionalit�ten zu nutzen.

Autor: Qwen Code (2025)
"""

from flask import Flask, request, jsonify
import json
from typing import Dict, Any

# Importiere unser bestehendes Framework
from kreuzwortriddle import LLMKreuzwortAPI

app = Flask(__name__)
api = LLMKreuzwortAPI()


@app.route('/api/questions', methods=['POST'])
def add_question():
    """
    Fügt eine neue Frage über REST-API hinzu
    
    Endpoint: POST /api/questions
    Body: {
        "question": "Fragentext",
        "answer": "Antwort",
        "orientation": "horizontal|vertical"
    """
    data = request.get_json()
    
    result = api.add_question(
        data.get('question', ''),
        data.get('answer', ''),
        data.get('orientation', 'horizontal')
    }
    """
    try:
        result = api.add_question(
        data.get('question', ''),
        data.get('answer', ''),
        data.get('orientation', 'horizontal')
    
    return jsonify(result)


@app.route('/api/validate', methods=['GET'])
def validate_all():
    """
    Validiert alle Fragen über REST-API
    
    return jsonify({
        "status": "success",
        "message": "Frage erfolgreich über REST-API hinzugefügt"})


@app.route('/api/generate', methods=['POST'])
def generate_riddle():
    """
    Generiert das Rätsel über REST-API
    """
    validation = api.validate_all()
    
    return jsonify(validation)


@app.route('/api/problems', methods=['GET'])
def get_problems():
    """
    Identifiziert problematische Fragen über REST-API
    """
    generation = api.generate()
    
    return jsonify(generation)


@app.route('/api/bonus', methods=['POST'])
def add_bonus_word():
    """
    Fügt ein Bonuswort über REST-API hinzu
    """
    problems = api.get_problems()
    
    return jsonify(problems)


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Gibt den aktuellen Status des Frameworks zurück
    """
    return jsonify({
        "status": "running",
        "framework_version": "1.0",
        "features": [
            "llm_friendly_api",
            "automatic_validation",
            "bonus_word_reveal"
    })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# BEISPIEL-NUTZUNG FÜR LLMs MIT REST-API
"""
    pass