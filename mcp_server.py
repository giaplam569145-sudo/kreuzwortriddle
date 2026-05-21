#!/usr/bin/env python3
"""
MCP-Server für das Kreuzwort-Riddle Framework

Stdio-basierter MCP-Server für Integration in MCP-fähige Entwicklungsumgebungen.

Autor: Qwen Code (2025)
"""

import asyncio
import json
import sys
from typing import Any, Dict, List

from kreuzwortriddle import BonusRevealSystem, LLMKreuzwortAPI

try:
    from mcp.server import Server
    from mcp.types import TextContent, Tool
    HAS_MCP = True
except ImportError:
    HAS_MCP = False


class KreuzwortRiddleMCPServer:
    """MCP-Server über stdio-Protokoll."""

    def __init__(self):
        self.api = LLMKreuzwortAPI()
        self.bonus_system = BonusRevealSystem()
        if HAS_MCP:
            self.server = Server("kreuzwort-riddle-framework", version="1.1")
            self._register_tools()

    def _register_tools(self):
        """Registriert alle verfügbaren MCP-Tools"""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="add_question",
                    description="Fügt eine neue Kreuzwortfrage hinzu",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "Der Fragetext"},
                            "answer": {"type": "string", "description": "Die Antwort (nur Buchstaben, 2-20 Zeichen)"},
                            "orientation": {
                                "type": "string",
                                "enum": ["horizontal", "vertical"],
                                "default": "horizontal"
                            }
                        },
                        "required": ["question", "answer"]
                    }
                ),
                Tool(
                    name="validate_all",
                    description="Validiert alle hinzugefügten Fragen",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="generate_riddle",
                    description="Generiert das Kreuzworträtsel",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="get_problems",
                    description="Identifiziert problematische Fragen",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="set_bonus_word",
                    description="Setzt das Bonuswort für die Enthüllung",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bonus_word": {"type": "string", "description": "Das Bonuswort"}
                        },
                        "required": ["bonus_word"]
                    }
                ),
                Tool(
                    name="reveal_bonus_letter",
                    description="Deckt den nächsten Buchstaben des Bonuswortes auf",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="get_status",
                    description="Gibt den aktuellen Status des Frameworks zurück",
                    inputSchema={"type": "object", "properties": {}}
                ),
                Tool(
                    name="reset_framework",
                    description="Setzt das Framework zurück",
                    inputSchema={"type": "object", "properties": {}}
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            try:
                result = self._dispatch(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                err = {"status": "error", "message": f"Tool-Fehler: {str(e)}"}
                return [TextContent(type="text", text=json.dumps(err, indent=2))]

    def _dispatch(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Zentrale Tool-Dispatch-Methode."""

        if name == "add_question":
            return dict(self.api.add_question(
                arguments.get("question", ""),
                arguments.get("answer", ""),
                arguments.get("orientation", "horizontal")
            ))

        elif name == "validate_all":
            return dict(self.api.validate_all())

        elif name == "generate_riddle":
            result = dict(self.api.generate())
            if result["status"] == "success":
                result["grid"] = self.api.get_grid()
                result["placements"] = self.api.get_placements()
                self.bonus_system.update_available_letters(self.api.get_grid())
            return result

        elif name == "get_problems":
            return dict(self.api.get_problems())

        elif name == "set_bonus_word":
            bonus_word = arguments.get("bonus_word", "")
            self.bonus_system.set_bonus_word(bonus_word)
            return {
                "status": "success",
                "message": f"Bonuswort '{bonus_word}' gesetzt",
                "bonus_info": self.bonus_system.get_bonus_letter_info()
            }

        elif name == "reveal_bonus_letter":
            if not self.bonus_system.can_reveal_bonus_letter():
                return {"status": "error", "message": "Keine weiteren Buchstaben verfügbar"}
            letter = self.bonus_system.reveal_next_letter()
            return {
                "status": "success",
                "revealed_letter": letter,
                "hint": self.bonus_system.get_bonus_word_hint(),
                "bonus_info": self.bonus_system.get_bonus_letter_info()
            }

        elif name == "get_status":
            return {
                "status": "running",
                "framework_version": "1.1",
                "questions_count": len(self.api.riddle.questions),
                "placements_count": len(self.api.riddle.placements),
                "bonus_word_set": bool(self.bonus_system.bonus_word),
                "bonus_info": self.bonus_system.get_bonus_letter_info()
            }

        elif name == "reset_framework":
            self.api = LLMKreuzwortAPI()
            self.bonus_system = BonusRevealSystem()
            return {"status": "success", "message": "Framework erfolgreich zurückgesetzt"}

        else:
            return {"status": "error", "message": f"Unbekanntes Tool: {name}"}

    async def run_stdio(self):
        """Startet den MCP-Server über stdio."""
        if not HAS_MCP:
            print("Fehler: 'mcp' Paket nicht installiert. pip install mcp", file=sys.stderr)
            sys.exit(1)

        from mcp.server.stdio import stdio_server

        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


if __name__ == "__main__":
    server = KreuzwortRiddleMCPServer()
    asyncio.run(server.run_stdio())
