#!/usr/bin/env python3
"""MCP Server for the Kreuzwort-Riddle Framework.

Enables the integration of the framework into MCP-enabled development
environments.

Author: Qwen Code (2025)
"""

import json
import asyncio
from typing import Dict, Any, List
from mcp.server import Server
from mcp.server.models import InitializationOptions
from mcp.types import Tool, TextContent

from kreuzwortriddle import LLMKreuzwortAPI, BonusRevealSystem


class KreuzwortRiddleMCPServer:
    """MCP server that exposes the framework's functionalities via MCP.

    This class provides an MCP-compatible interface to the Kreuzwort-Riddle
    framework, allowing MCP-enabled clients to interact with the crossword
    puzzle generation and bonus word features.
    """

    def __init__(self):
        """Initializes the KreuzwortRiddleMCPServer.

        This sets up the API, bonus system, and the MCP server, and
        registers the available tools.
        """
        self.api = LLMKreuzwortAPI()
        self.bonus_system = BonusRevealSystem()
        self.server = Server("kreuzwort-riddle-framework", InitializationOptions())

        # Registriere die Tools
        self._register_tools()

    def _register_tools(self):
        """Registers all available MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Lists all available tools.

            Returns:
                A list of Tool objects that can be called by an MCP client.
            """
            return [
                Tool(
                    name="add_question",
                    description="Fügt eine neue Kreuzwortfrage hinzu",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "question": {
                                "type": "string",
                                "description": "Der Fragetext"
                            },
                            "answer": {
                                "type": "string",
                                "description": "Die Antwort (nur Buchstaben, 2-20 Zeichen)"
                            },
                            "orientation": {
                                "type": "string",
                                "enum": ["horizontal", "vertical"],
                                "description": "Ausrichtung des Wortes",
                                "default": "horizontal"
                            }
                        },
                        "required": ["question", "answer"]
                    }
                ),
                Tool(
                    name="validate_all",
                    description="Validiert alle hinzugefügten Fragen",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="generate_riddle",
                    description="Generiert das Kreuzworträtsel",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_problems",
                    description="Identifiziert problematische Fragen",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="set_bonus_word",
                    description="Setzt das Bonuswort für die Enthüllung",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "bonus_word": {
                                "type": "string",
                                "description": "Das Bonuswort"
                            },
                            "description": {
                                "type": "string",
                                "description": "Beschreibung des Bonuswortes"
                            }
                        },
                        "required": ["bonus_word"]
                    }
                ),
                Tool(
                    name="reveal_bonus_letter",
                    description="Deckt den nächsten Buchstaben des Bonuswortes auf",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="get_status",
                    description="Gibt den aktuellen Status des Frameworks zurück",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                ),
                Tool(
                    name="reset_framework",
                    description="Setzt das Framework zurück",
                    inputSchema={
                        "type": "object",
                        "properties": {}
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Processes tool calls.

            Args:
                name: The name of the tool to call.
                arguments: The arguments for the tool.

            Returns:
                A list of TextContent objects containing the result of the
                tool call.
            """
            try:
                if name == "add_question":
                    result = self.api.add_question(
                        arguments.get("question", ""),
                        arguments.get("answer", ""),
                        arguments.get("orientation", "horizontal")
                    )
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "validate_all":
                    result = self.api.validate_all()
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "generate_riddle":
                    result = self.api.generate()
                    if result["status"] == "success":
                        result["grid"] = self.api.get_grid()
                        result["placements"] = self.api.get_placements()
                        self.bonus_system.update_available_letters(self.api.get_grid())
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "get_problems":
                    result = self.api.get_problems()
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "set_bonus_word":
                    bonus_word = arguments.get("bonus_word", "")
                    self.bonus_system.set_bonus_word(bonus_word)
                    result = {
                        "status": "success",
                        "message": f"Bonuswort '{bonus_word}' gesetzt",
                        "bonus_info": self.bonus_system.get_bonus_letter_info()
                    }
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "reveal_bonus_letter":
                    if not self.bonus_system.can_reveal_bonus_letter():
                        result = {
                            "status": "error",
                            "message": "Keine weiteren Buchstaben verfügbar"
                        }
                    else:
                        letter = self.bonus_system.reveal_next_letter()
                        result = {
                            "status": "success",
                            "revealed_letter": letter,
                            "hint": self.bonus_system.get_bonus_word_hint(),
                            "bonus_info": self.bonus_system.get_bonus_letter_info()
                        }
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "get_status":
                    result = {
                        "status": "running",
                        "framework_version": "1.0",
                        "questions_count": len(self.api.riddle.questions),
                        "placements_count": len(self.api.riddle.placements),
                        "bonus_word_set": bool(self.bonus_system.bonus_word),
                        "bonus_info": self.bonus_system.get_bonus_letter_info()
                    }
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                elif name == "reset_framework":
                    self.api = LLMKreuzwortAPI()
                    self.bonus_system = BonusRevealSystem()
                    result = {
                        "status": "success",
                        "message": "Framework erfolgreich zurückgesetzt"
                    }
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

                else:
                    result = {
                        "status": "error",
                        "message": f"Unbekanntes Tool: {name}"
                    }
                    return [TextContent(type="text", text=json.dumps(result, indent=2))]

            except Exception as e:
                error_result = {
                    "status": "error",
                    "message": f"Tool-Fehler: {str(e)}"
                }
                return [TextContent(type="text", text=json.dumps(error_result, indent=2))]

    async def run(self, host: str = "localhost", port: int = 8000):
        """Starts the MCP server.

        Args:
            host: The host to run the server on.
            port: The port to run the server on.
        """
        print(f"Kreuzwort-Riddle MCP-Server startet auf {host}:{port}")

        # Hier würde die eigentliche MCP-Server-Initialisierung erfolgen
        # Dies ist eine vereinfachte Implementierung
        import uvicorn
        from fastapi import FastAPI

        app = FastAPI(title="Kreuzwort-Riddle MCP Server")

        @app.post("/mcp/call")
        async def mcp_call(request: Dict[str, Any]):
            """MCP-compatible endpoint.

            Args:
                request: The request from the MCP client.

            Returns:
                The results of the tool call.
            """
            tool_name = request.get("tool")
            arguments = request.get("arguments", {})

            # Verwende die bestehende Tool-Logik
            results = await call_tool(tool_name, arguments)
            return {"results": results}

        await uvicorn.run(app, host=host, port=port)


# MCP-SERVER KONFIGURATION
if __name__ == "__main__":
    """
    Starts the MCP server for the framework.
    """
    server = KreuzwortRiddleMCPServer()

    # Starte den Server
    asyncio.run(server.run())
