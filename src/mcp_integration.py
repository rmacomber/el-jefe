#!/usr/bin/env python3
"""
Direct MCP Integration for El Jefe

Provides direct integration with available MCP tools (memory and context7)
that are available in the Claude Code environment.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional


class MemoryMCPIntegration:
    """Direct integration with Memory MCP server."""

    def __init__(self):
        self.available = True  # We know it's available from the tool list

    async def create_entity(self, name: str, entity_type: str, observations: List[str]) -> Dict[str, Any]:
        """Create a new entity in the knowledge graph."""
        try:
            entities = [{
                "name": name,
                "entityType": entity_type,
                "observations": observations
            }]
            result = await mcp__memory.create_entities(entities=entities)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def create_relation(self, from_entity: str, to_entity: str, relation_type: str) -> Dict[str, Any]:
        """Create a relation between two entities."""
        try:
            relations = [{
                "from": from_entity,
                "to": to_entity,
                "relationType": relation_type
            }]
            result = await mcp__memory.create_relations(relations=relations)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def search_knowledge(self, query: str) -> Dict[str, Any]:
        """Search the knowledge graph."""
        try:
            result = await mcp__memory.search_nodes(query=query)
            return {"success": True, "results": result}
        except Exception as e:
            return {"error": str(e)}

    async def add_observations(self, entity_name: str, observations: List[str]) -> Dict[str, Any]:
        """Add observations to an entity."""
        try:
            obs_data = [{
                "entityName": entity_name,
                "contents": observations
            }]
            result = await mcp__memory.add_observations(observations=obs_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}


class Context7MCPIntegration:
    """Direct integration with Context7 MCP server."""

    def __init__(self):
        self.available = True  # We know it's available from the tool list

    async def resolve_library(self, library_name: str) -> Dict[str, Any]:
        """Resolve library name to Context7-compatible ID."""
        try:
            result = await mcp__context7.resolve_library_id(libraryName=library_name)
            return {"success": True, "libraries": result}
        except Exception as e:
            return {"error": str(e)}

    async def get_library_docs(self, library_id: str, topic: Optional[str] = None, mode: str = "code") -> Dict[str, Any]:
        """Get library documentation."""
        try:
            params = {"context7CompatibleLibraryID": library_id}
            if topic:
                params["topic"] = topic
            if mode:
                params["mode"] = mode

            result = await mcp__context7.get_library_docs(**params)
            return {"success": True, "documentation": result}
        except Exception as e:
            return {"error": str(e)}


class MCPToolIntegration:
    """Manages direct MCP tool integration for El Jefe."""

    def __init__(self):
        self.memory_integration = MemoryMCPIntegration()
        self.context7_integration = Context7MCPIntegration()
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize the tool functions that can be used by agents."""
        self.tools = {
            "memory_create_entity": self.memory_create_entity_tool,
            "memory_create_relation": self.memory_create_relation_tool,
            "memory_search": self.memory_search_tool,
            "memory_add_observations": self.memory_add_observations_tool,
            "context7_resolve_library": self.context7_resolve_library_tool,
            "context7_get_docs": self.context7_get_docs_tool
        }

    async def memory_create_entity_tool(self, name: str, entity_type: str, observations: List[str]) -> str:
        """Memory MCP tool: Create entity."""
        result = await self.memory_integration.create_entity(name, entity_type, observations)
        if result.get("success"):
            return f"✅ Created entity '{name}' with {len(observations)} observations"
        return f"❌ Failed: {result.get('error')}"

    async def memory_create_relation_tool(self, from_entity: str, to_entity: str, relation_type: str) -> str:
        """Memory MCP tool: Create relation."""
        result = await self.memory_integration.create_relation(from_entity, to_entity, relation_type)
        if result.get("success"):
            return f"✅ Created relation: {from_entity} -> {relation_type} -> {to_entity}"
        return f"❌ Failed: {result.get('error')}"

    async def memory_search_tool(self, query: str) -> str:
        """Memory MCP tool: Search knowledge graph."""
        result = await self.memory_integration.search_knowledge(query)
        if result.get("success"):
            search_data = result.get("results", {})
            if isinstance(search_data, dict) and "nodes" in search_data:
                nodes = search_data["nodes"]
                if nodes:
                    response = f"🔍 Found {len(nodes)} entities:\n"
                    for node in nodes[:3]:
                        response += f"📌 {node.get('name', 'Unknown')}\n"
                    return response
            return "🔍 No results found"
        return f"❌ Failed: {result.get('error')}"

    async def memory_add_observations_tool(self, entity_name: str, observations: List[str]) -> str:
        """Memory MCP tool: Add observations."""
        result = await self.memory_integration.add_observations(entity_name, observations)
        if result.get("success"):
            return f"✅ Added {len(observations)} observations to '{entity_name}'"
        return f"❌ Failed: {result.get('error')}"

    async def context7_resolve_library_tool(self, library_name: str) -> str:
        """Context7 MCP tool: Resolve library."""
        result = await self.context7_integration.resolve_library(library_name)
        if result.get("success"):
            libraries = result.get("libraries", [])
            if libraries:
                return f"📚 Found {len(libraries)} libraries for '{library_name}'"
            return "📚 No libraries found"
        return f"❌ Failed: {result.get('error')}"

    async def context7_get_docs_tool(self, library_id: str, topic: Optional[str] = None, mode: str = "code") -> str:
        """Context7 MCP tool: Get docs."""
        result = await self.context7_integration.get_library_docs(library_id, topic, mode)
        if result.get("success"):
            docs = result.get("documentation", "")
            return f"📖 Documentation for '{library_id}':\n{docs[:500]}..." if len(docs) > 500 else f"📖 Documentation for '{library_id}':\n{docs}"
        return f"❌ Failed: {result.get('error')}"

    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tool names."""
        return list(self.tools.keys())

    def is_available(self) -> bool:
        """Check if MCP tools are available."""
        return len(self.tools) > 0

    async def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """Execute an MCP tool."""
        if tool_name in self.tools:
            return await self.tools[tool_name](**kwargs)
        return f"❌ Tool '{tool_name}' not available"


# Global MCP integration instance
_mcp_integration: Optional[MCPToolIntegration] = None


def get_mcp_integration() -> MCPToolIntegration:
    """Get the global MCP integration instance."""
    global _mcp_integration
    if _mcp_integration is None:
        _mcp_integration = MCPToolIntegration()
        print(f"🔧 MCP Integration: {_mcp_integration.is_available()} with {len(_mcp_integration.get_available_tools())} tools")
    return _mcp_integration