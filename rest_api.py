#!/usr/bin/env python3
"""
REST-API für das Kreuzwort-Riddle Framework

Ermöglicht LLMs ohne direkten Python-Zugriff die Framework-Funktionalitäten zu nutzen.

Autor: Qwen Code (2025)
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
    """
    Fügt eine neue Frage über REST-API hinzu
    
    Endpoint: POST /api/questions
    Body: {
        "question": "Fragentext",
        "answer": "Antwort",
        "orientation": "horizontal|vertical"
    }
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
    """
    Validiert alle Fragen über REST-API
    
    Endpoint: GET /api/validate
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
    """
    Generiert das Rätsel über REST-API
    
    Endpoint: POST /api/generate
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
    """
    Identifiziert problematische Fragen über REST-API
    
    Endpoint: GET /api/problems
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
    """
    Bonuswort-Funktionen über REST-API
    
    POST: Setzt Bonuswort
    GET: Gibt Bonuswort-Status zurück
    
    Endpoint: POST /api/bonus
    Body: {"bonus_word": "EUROPA", "description": "Kontinent"}
    
    Endpoint: GET /api/bonus
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
    """
    Deckt nächsten Buchstaben des Bonuswortes auf
    
    Endpoint: POST /api/bonus/reveal
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
    """
    Gibt den aktuellen Status des Frameworks zurück
    
    Endpoint: GET /api/status
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
    """
    Setzt das Framework zurück
    
    Endpoint: POST /api/reset
    
    Hinweis: Verwendet `global` — nicht thread-safe.
    Für Produktion eine pro-Session-Instanz oder eine WSGI-Lösung verwenden.
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
    return jsonify({
        "status": "error",
        "message": "Endpoint nicht gefunden"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "status": "error",
        "message": "Interner Serverfehler"
    }), 500


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)


# BEISPIEL-NUTZUNG FÜR LLMs MIT REST-API
"""
Beispiel für die Nutzung der REST-API:

1. Frage hinzufügen:
POST /api/questions
{
    "question": "Hauptstadt von Deutschland",
    "answer": "Berlin",
    "orientation": "horizontal"
}

2. Validieren:
GET /api/validate

3. Generieren:
POST /api/generate

4. Bonuswort setzen:
POST /api/bonus
{
    "bonus_word": "EUROPA",
    "description": "Kontinent"
}

5. Bonusbuchstabe aufdecken:
POST /api/bonus/reveal

6. Status abfragen:
GET /api/status
"""