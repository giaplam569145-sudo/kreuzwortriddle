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

from kreuzwortriddle import LLMKreuzwortAPI

class KreuzwortRiddleMCPServer:
    """MCP server that exposes the framework's functionalities via MCP."""

    def __init__(self):
        """Initializes the KreuzwortRiddleMCPServer."""
        self.api = LLMKreuzwortAPI()
        self.server = Server("kreuzwort-riddle-framework", InitializationOptions())
        self._register_tools()

    def _register_tools(self):
        """Registers all available MCP tools."""

        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Lists all available tools."""
            return [
                Tool(name="add_question", description="Adds a new crossword question"),
                Tool(name="validate_all", description="Validates all added questions"),
                Tool(name="generate_riddle", description="Generates the crossword puzzle"),
                Tool(name="get_problems", description="Identifies problematic questions"),
                Tool(name="set_bonus_word", description="Sets the bonus word for the reveal"),
                Tool(name="reveal_bonus_letter", description="Reveals the next letter of the bonus word"),
                Tool(name="get_status", description="Returns the current status of the framework"),
                Tool(name="reset_framework", description="Resets the framework"),
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Processes tool calls."""
            try:
                result = self._dispatch_tool(name, arguments)
                return [TextContent(type="text", text=json.dumps(result, indent=2))]
            except Exception as e:
                return [TextContent(type="text", text=json.dumps({"status": "error", "message": str(e)}, indent=2))]

    def _dispatch_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Dispatches tool calls to the appropriate API methods."""
        if name == "add_question":
            return self.api.add_question(
                arguments.get("question", ""),
                arguments.get("answer", ""),
                arguments.get("orientation", "horizontal")
            )
        elif name == "validate_all":
            return self.api.validate_all()
        elif name == "generate_riddle":
            result = self.api.generate()
            if result["status"] == "success":
                result["grid"] = self.api.get_grid()
                result["placements"] = self.api.get_placements()
            return result
        elif name == "get_problems":
            return self.api.get_problems()
        elif name == "set_bonus_word":
            bonus_word = arguments.get("bonus_word", "")
            self.api.set_bonus_word(bonus_word)
            return {"status": "success", "message": f"Bonus word '{bonus_word}' set"}
        elif name == "reveal_bonus_letter":
            letter = self.api.reveal_next_bonus_letter()
            if letter:
                return {"status": "success", "revealed_letter": letter, "hint": self.api.get_bonus_word_hint()}
            else:
                return {"status": "error", "message": "No more letters available to reveal"}
        elif name == "get_status":
            return {
                "status": "running",
                "framework_version": "1.0",
                "questions_count": len(self.api.riddle.questions),
                "placements_count": len(self.api.riddle.placements),
                "bonus_word_set": bool(self.api.riddle.bonus_word),
            }
        elif name == "reset_framework":
            self.api = LLMKreuzwortAPI()
            return {"status": "success", "message": "Framework reset successfully"}
        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}

    async def run(self, host: str = "localhost", port: int = 8000):
        """Starts the MCP server."""
        print(f"Kreuzwort-Riddle MCP server starting on {host}:{port}")
        # This is a simplified implementation. A real implementation would use the MCP server.
        import uvicorn
        from fastapi import FastAPI

        app = FastAPI(title="Kreuzwort-Riddle MCP Server")

        @app.post("/mcp/call")
        async def mcp_call(request: Dict[str, Any]):
            tool_name = request.get("tool")
            arguments = request.get("arguments", {})
            results = await self.server.call_tool(tool_name, arguments)
            return {"results": results}

        await uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    server = KreuzwortRiddleMCPServer()
    asyncio.run(server.run())
