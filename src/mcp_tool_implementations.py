#!/usr/bin/env python3
"""
MCP Tool Implementations for Claude Agent SDK

Provides actual tool implementations that can be used by the Claude Agent SDK
with Memory MCP and Context7 MCP servers.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path


def create_memory_create_entity_tool():
    """Create a memory_create_entity tool for the Claude Agent SDK."""

    async def memory_create_entity(name: str, entity_type: str, observations: List[str]) -> str:
        """Create a new entity in the knowledge graph with observations."""
        try:
            from .mcp_tools import get_mcp_tool_manager
            mcp_manager = get_mcp_tool_manager()

            if not mcp_manager.memory_tools.available:
                return "❌ Memory MCP server is not available"

            result = await mcp_manager.memory_tools.create_entity(name, entity_type, observations)

            if result.get("success"):
                return f"✅ Successfully created entity '{name}' of type '{entity_type}' with {len(observations)} observations"
            else:
                return f"❌ Failed to create entity: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error creating entity: {str(e)}"

    return {
        "name": "memory_create_entity",
        "description": "Create a new entity in the knowledge graph with observations",
        "parameters": {
            "name": {"type": "string", "description": "The name of the entity"},
            "entity_type": {"type": "string", "description": "The type/category of the entity"},
            "observations": {"type": "array", "items": {"type": "string"}, "description": "List of observations about the entity"}
        },
        "function": memory_create_entity
    }


def create_memory_create_relation_tool():
    """Create a memory_create_relation tool for the Claude Agent SDK."""

    async def memory_create_relation(from_entity: str, to_entity: str, relation_type: str) -> str:
        """Create a relation between two entities in the knowledge graph."""
        try:
            from .mcp_tools import get_mcp_tool_manager
            mcp_manager = get_mcp_tool_manager()

            if not mcp_manager.memory_tools.available:
                return "❌ Memory MCP server is not available"

            result = await mcp_manager.memory_tools.create_relation(from_entity, to_entity, relation_type)

            if result.get("success"):
                return f"✅ Successfully created relation: '{from_entity}' -> '{relation_type}' -> '{to_entity}'"
            else:
                return f"❌ Failed to create relation: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error creating relation: {str(e)}"

    return {
        "name": "memory_create_relation",
        "description": "Create a relation between two entities in the knowledge graph",
        "parameters": {
            "from_entity": {"type": "string", "description": "The name of the source entity"},
            "to_entity": {"type": "string", "description": "The name of the target entity"},
            "relation_type": {"type": "string", "description": "The type of relation"}
        },
        "function": memory_create_relation
    }


def create_memory_search_tool():
    """Create a memory_search tool for the Claude Agent SDK."""

    async def memory_search(query: str) -> str:
        """Search the knowledge graph for relevant information."""
        try:
            from .mcp_tools import get_mcp_tool_manager
            mcp_manager = get_mcp_tool_manager()

            if not mcp_manager.memory_tools.available:
                return "❌ Memory MCP server is not available"

            result = await mcp_manager.memory_tools.search_knowledge(query)

            if result.get("success"):
                search_results = result.get("results", {})
                if isinstance(search_results, dict) and "nodes" in search_results:
                    nodes = search_results["nodes"]
                    if nodes:
                        response = f"🔍 Found {len(nodes)} relevant entities:\n\n"
                        for node in nodes[:5]:  # Limit to top 5 results
                            response += f"📌 {node.get('name', 'Unknown')}\n"
                            if 'entityType' in node:
                                response += f"   Type: {node['entityType']}\n"
                            if 'observations' in node and node['observations']:
                                response += f"   Info: {'; '.join(str(obs) for obs in node['observations'][:2])}\n"
                            response += "\n"
                        return response
                    else:
                        return "🔍 No relevant information found in the knowledge graph"
                else:
                    return f"🔍 Search completed: {json.dumps(search_results, indent=2)}"
            else:
                return f"❌ Failed to search knowledge graph: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error searching knowledge graph: {str(e)}"

    return {
        "name": "memory_search",
        "description": "Search the knowledge graph for relevant information",
        "parameters": {
            "query": {"type": "string", "description": "Search query to find relevant information"}
        },
        "function": memory_search
    }


def create_memory_add_observations_tool():
    """Create a memory_add_observations tool for the Claude Agent SDK."""

    async def memory_add_observations(entity_name: str, observations: List[str]) -> str:
        """Add observations to an existing entity."""
        try:
            from .mcp_tools import get_mcp_tool_manager
            mcp_manager = get_mcp_tool_manager()

            if not mcp_manager.memory_tools.available:
                return "❌ Memory MCP server is not available"

            result = await mcp_manager.memory_tools.add_observations(entity_name, observations)

            if result.get("success"):
                return f"✅ Successfully added {len(observations)} observations to entity '{entity_name}'"
            else:
                return f"❌ Failed to add observations: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error adding observations: {str(e)}"

    return {
        "name": "memory_add_observations",
        "description": "Add observations to an existing entity in the knowledge graph",
        "parameters": {
            "entity_name": {"type": "string", "description": "The name of the entity to add observations to"},
            "observations": {"type": "array", "items": {"type": "string"}, "description": "List of observations to add"}
        },
        "function": memory_add_observations
    }


def create_context7_resolve_library_tool():
    """Create a context7_resolve_library tool for the Claude Agent SDK."""

    async def context7_resolve_library(library_name: str) -> str:
        """Find Context7-compatible library IDs for a library name."""
        try:
            from .mcp_tools import get_mcp_tool_manager
            mcp_manager = get_mcp_tool_manager()

            if not mcp_manager.context7_tools.available:
                return "❌ Context7 MCP server is not available"

            result = await mcp_manager.context7_tools.resolve_library(library_name)

            if result.get("success"):
                libraries = result.get("libraries", [])
                if libraries:
                    response = f"📚 Found {len(libraries)} libraries matching '{library_name}':\n\n"
                    for lib in libraries[:3]:  # Limit to top 3 results
                        response += f"📖 {lib.get('name', 'Unknown')}\n"
                        if lib.get('description'):
                            response += f"   {lib['description'][:100]}...\n"
                        response += "\n"
                    return response
                else:
                    return f"📚 No libraries found matching '{library_name}'"
            else:
                return f"❌ Failed to resolve library: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error resolving library: {str(e)}"

    return {
        "name": "context7_resolve_library",
        "description": "Find Context7-compatible library IDs for a library name",
        "parameters": {
            "library_name": {"type": "string", "description": "Name of the library to search for"}
        },
        "function": context7_resolve_library
    }


def create_context7_get_docs_tool():
    """Create a context7_get_docs tool for the Claude Agent SDK."""

    async def context7_get_docs(library_id: str, topic: Optional[str] = None, mode: str = "code") -> str:
        """Get up-to-date documentation for a library."""
        try:
            from .mcp_tools import get_mcp_tool_manager
            mcp_manager = get_mcp_tool_manager()

            if not mcp_manager.context7_tools.available:
                return "❌ Context7 MCP server is not available"

            result = await mcp_manager.context7_tools.get_library_documentation(library_id, topic, mode)

            if result.get("success"):
                docs = result.get("documentation", "")
                if docs:
                    return f"📖 Documentation for library '{library_id}':\n\n{docs}"
                else:
                    return f"📖 No documentation found for library '{library_id}'"
            else:
                return f"❌ Failed to get documentation: {result.get('error', 'Unknown error')}"

        except Exception as e:
            return f"❌ Error getting documentation: {str(e)}"

    return {
        "name": "context7_get_docs",
        "description": "Get up-to-date documentation for a library (Context7-compatible library ID)",
        "parameters": {
            "library_id": {"type": "string", "description": "Context7-compatible library ID (e.g., /org/project)"},
            "topic": {"type": "string", "description": "Specific topic to focus documentation on (optional)"},
            "mode": {"type": "string", "description": "Documentation mode: 'code' for API references or 'info' for guides (default: code)"}
        },
        "function": context7_get_docs
    }


def get_all_mcp_tools() -> List[Dict[str, Any]]:
    """Get all available MCP tool implementations."""
    tools = []

    try:
        from .mcp_tools import get_mcp_tool_manager
        mcp_manager = get_mcp_tool_manager()

        if mcp_manager.memory_tools.available:
            tools.extend([
                create_memory_create_entity_tool(),
                create_memory_create_relation_tool(),
                create_memory_search_tool(),
                create_memory_add_observations_tool()
            ])

        if mcp_manager.context7_tools.available:
            tools.extend([
                create_context7_resolve_library_tool(),
                create_context7_get_docs_tool()
            ])

        print(f"🔧 Created {len(tools)} MCP tool implementations")

    except Exception as e:
        print(f"⚠️  Failed to create MCP tool implementations: {e}")

    return tools