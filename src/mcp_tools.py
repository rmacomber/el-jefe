#!/usr/bin/env python3
"""
MCP Tool Wrappers for El Jefe

Provides wrappers for Memory MCP and Context7 MCP servers to be used by El Jefe agents.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path


class MemoryMCPTools:
    """Wrapper for Memory MCP server tools."""

    def __init__(self):
        """Initialize Memory MCP tools."""
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Memory MCP server is available."""
        try:
            # Test by checking if we can import the required tools
            from mcp__memory import create_entities, create_relations, add_observations, read_graph, search_nodes
            return True
        except ImportError:
            return False

    async def create_entity(self, name: str, entity_type: str, observations: List[str]) -> Dict[str, Any]:
        """Create a new entity in the knowledge graph."""
        if not self.available:
            return {"error": "Memory MCP server not available"}

        try:
            from mcp__memory import create_entities
            entity_data = [{
                "name": name,
                "entityType": entity_type,
                "observations": observations
            }]
            result = await create_entities(entities=entity_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def create_relation(self, from_entity: str, to_entity: str, relation_type: str) -> Dict[str, Any]:
        """Create a relation between two entities."""
        if not self.available:
            return {"error": "Memory MCP server not available"}

        try:
            from mcp__memory import create_relations
            relation_data = [{
                "from": from_entity,
                "to": to_entity,
                "relationType": relation_type
            }]
            result = await create_relations(relations=relation_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def add_observations(self, entity_name: str, observations: List[str]) -> Dict[str, Any]:
        """Add observations to an existing entity."""
        if not self.available:
            return {"error": "Memory MCP server not available"}

        try:
            from mcp__memory import add_observations
            obs_data = [{
                "entityName": entity_name,
                "contents": observations
            }]
            result = await add_observations(observations=obs_data)
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def search_knowledge(self, query: str) -> Dict[str, Any]:
        """Search the knowledge graph for relevant information."""
        if not self.available:
            return {"error": "Memory MCP server not available"}

        try:
            from mcp__memory import search_nodes
            result = await search_nodes(query=query)
            return {"success": True, "results": result}
        except Exception as e:
            return {"error": str(e)}

    async def read_graph(self) -> Dict[str, Any]:
        """Read the entire knowledge graph."""
        if not self.available:
            return {"error": "Memory MCP server not available"}

        try:
            from mcp__memory import read_graph
            result = await read_graph()
            return {"success": True, "graph": result}
        except Exception as e:
            return {"error": str(e)}


class Context7MCPTools:
    """Wrapper for Context7 MCP server tools."""

    def __init__(self):
        """Initialize Context7 MCP tools."""
        self.available = self._check_availability()

    def _check_availability(self) -> bool:
        """Check if Context7 MCP server is available."""
        try:
            # Test by checking if we can import the required tools
            from mcp__context7 import resolve_library_id, get_library_docs
            return True
        except ImportError:
            return False

    async def resolve_library(self, library_name: str) -> Dict[str, Any]:
        """Resolve a library name to get Context7-compatible library ID."""
        if not self.available:
            return {"error": "Context7 MCP server not available"}

        try:
            from mcp__context7 import resolve_library_id
            result = await resolve_library_id(libraryName=library_name)
            return {"success": True, "libraries": result}
        except Exception as e:
            return {"error": str(e)}

    async def get_library_documentation(self, library_id: str, topic: Optional[str] = None, mode: str = "code") -> Dict[str, Any]:
        """Get up-to-date documentation for a library."""
        if not self.available:
            return {"error": "Context7 MCP server not available"}

        try:
            from mcp__context7 import get_library_docs
            params = {"context7CompatibleLibraryID": library_id}
            if topic:
                params["topic"] = topic
            if mode:
                params["mode"] = mode

            result = await get_library_docs(**params)
            return {"success": True, "documentation": result}
        except Exception as e:
            return {"error": str(e)}

    async def search_libraries(self, query: str) -> Dict[str, Any]:
        """Search for libraries using Context7."""
        if not self.available:
            return {"error": "Context7 MCP server not available"}

        # First resolve the library to get matches
        resolve_result = await self.resolve_library(query)
        if not resolve_result.get("success"):
            return resolve_result

        return {"success": True, "search_results": resolve_result.get("libraries", [])}


class MCPToolManager:
    """Manages all MCP tools for El Jefe agents."""

    def __init__(self):
        """Initialize MCP tool manager."""
        self.memory_tools = MemoryMCPTools()
        self.context7_tools = Context7MCPTools()
        self._tool_registry = self._build_tool_registry()

    def _build_tool_registry(self) -> Dict[str, callable]:
        """Build a registry of available MCP tools."""
        registry = {}

        # Memory MCP tools
        if self.memory_tools.available:
            registry.update({
                "memory_create_entity": self.memory_tools.create_entity,
                "memory_create_relation": self.memory_tools.create_relation,
                "memory_add_observations": self.memory_tools.add_observations,
                "memory_search": self.memory_tools.search_knowledge,
                "memory_read_graph": self.memory_tools.read_graph
            })

        # Context7 MCP tools
        if self.context7_tools.available:
            registry.update({
                "context7_resolve_library": self.context7_tools.resolve_library,
                "context7_get_docs": self.context7_tools.get_library_documentation,
                "context7_search": self.context7_tools.search_libraries
            })

        return registry

    def get_available_tools(self) -> List[str]:
        """Get list of available MCP tool names."""
        return list(self._tool_registry.keys())

    def is_available(self) -> bool:
        """Check if any MCP tools are available."""
        return len(self._tool_registry) > 0

    async def execute_tool(self, tool_name: str, **kwargs) -> Dict[str, Any]:
        """Execute an MCP tool by name."""
        if tool_name not in self._tool_registry:
            return {"error": f"Tool '{tool_name}' not available"}

        try:
            result = await self._tool_registry[tool_name](**kwargs)
            return result
        except Exception as e:
            return {"error": f"Error executing tool '{tool_name}': {str(e)}"}

    def get_tool_descriptions(self) -> Dict[str, str]:
        """Get descriptions of available MCP tools."""
        descriptions = {
            "memory_create_entity": "Create a new entity in the knowledge graph with observations",
            "memory_create_relation": "Create a relation between two entities in the knowledge graph",
            "memory_add_observations": "Add observations to an existing entity",
            "memory_search": "Search the knowledge graph for relevant information",
            "memory_read_graph": "Read the entire knowledge graph",
            "context7_resolve_library": "Find Context7-compatible library IDs for a library name",
            "context7_get_docs": "Get up-to-date documentation for a library",
            "context7_search": "Search for libraries and their documentation"
        }

        return {name: desc for name, desc in descriptions.items() if name in self._tool_registry}


# Global MCP tool manager instance
_mcp_manager: Optional[MCPToolManager] = None


def get_mcp_tool_manager() -> MCPToolManager:
    """Get the global MCP tool manager instance."""
    global _mcp_manager
    if _mcp_manager is None:
        _mcp_manager = MCPToolManager()
        print(f"🔧 MCP Tool Manager: {len(_mcp_manager.get_available_tools())} tools available")
        if _mcp_manager.memory_tools.available:
            print("  ✅ Memory MCP server: Available")
        if _mcp_manager.context7_tools.available:
            print("  ✅ Context7 MCP server: Available")

    return _mcp_manager