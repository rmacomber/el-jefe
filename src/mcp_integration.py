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


class WebSearchMCPIntegration:
    """Direct integration with Web Search MCP servers."""

    def __init__(self):
        self.available = True  # We know it's available from the tool list

    async def search_web_prime(self, search_query: str, count: int = 10, search_recency_filter: str = "noLimit") -> Dict[str, Any]:
        """Search using WebSearchPrime MCP server."""
        try:
            result = await mcp__web-search-prime__webSearchPrime(
                searchQuery=search_query,
                count=count,
                searchRecencyFilter=search_recency_filter
            )
            return {"success": True, "results": result}
        except Exception as e:
            return {"error": str(e)}

    async def web_reader(self, url: str, return_format: str = "markdown", retain_images: bool = True) -> Dict[str, Any]:
        """Read and convert web content using ZAI Web Reader."""
        try:
            result = await mcp__zai-web-reader__webReader(
                url=url,
                returnFormat=return_format,
                retainImages=retain_images
            )
            return {"success": True, "content": result}
        except Exception as e:
            return {"error": str(e)}


class VisionMCPIntegration:
    """Direct integration with Vision MCP servers for image analysis."""

    def __init__(self):
        self.available = True

    async def analyze_image(self, image_source: str, prompt: str) -> Dict[str, Any]:
        """Analyze an image using AI vision."""
        try:
            # Try ZAI Vision Server first
            result = await mcp__zai-vision-server__analyze_image(
                imageSource=image_source,
                prompt=prompt
            )
            return {"success": True, "analysis": result}
        except Exception:
            try:
                # Fallback to ZAI MCP Server
                result = await mcp__zai-mcp-server__analyze_image(
                    imageSource=image_source,
                    prompt=prompt
                )
                return {"success": True, "analysis": result}
            except Exception as e:
                return {"error": str(e)}

    async def analyze_video(self, video_source: str, prompt: str) -> Dict[str, Any]:
        """Analyze a video using AI vision."""
        try:
            # Try ZAI Vision Server first
            result = await mcp__zai-vision-server__analyze_video(
                videoSource=video_source,
                prompt=prompt
            )
            return {"success": True, "analysis": result}
        except Exception:
            try:
                # Fallback to ZAI MCP Server
                result = await mcp__zai-mcp-server__analyze_video(
                    videoSource=video_source,
                    prompt=prompt
                )
                return {"success": True, "analysis": result}
            except Exception as e:
                return {"error": str(e)}


class BrowserAutomationMCPIntegration:
    """Direct integration with Browser Automation MCP servers."""

    def __init__(self):
        self.available = True

    async def navigate_to_url(self, url: str, browser_type: str = "chromium", width: int = 1280, height: int = 720) -> Dict[str, Any]:
        """Navigate to a URL using Playwright."""
        try:
            result = await mcp__executeautomation-playwright-server__playwright_navigate(
                url=url,
                browserType=browser_type,
                width=width,
                height=height
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def take_screenshot(self, name: str, full_page: bool = False) -> Dict[str, Any]:
        """Take a screenshot of the current page."""
        try:
            result = await mcp__executeautomation-playwright-server__playwright_screenshot(
                name=name,
                fullPage=full_page
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def click_element(self, selector: str) -> Dict[str, Any]:
        """Click an element on the page."""
        try:
            result = await mcp__executeautomation-playwright-server__playwright_click(
                selector=selector
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

    async def fill_input(self, selector: str, value: str) -> Dict[str, Any]:
        """Fill an input field."""
        try:
            result = await mcp__executeautomation-playwright-server__playwright_fill(
                selector=selector,
                value=value
            )
            return {"success": True, "result": result}
        except Exception as e:
            return {"error": str(e)}

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
        self.web_search_integration = WebSearchMCPIntegration()
        self.vision_integration = VisionMCPIntegration()
        self.browser_automation_integration = BrowserAutomationMCPIntegration()
        self._initialize_tools()

    def _initialize_tools(self):
        """Initialize the tool functions that can be used by agents."""
        self.tools = {
            # Memory tools
            "memory_create_entity": self.memory_create_entity_tool,
            "memory_create_relation": self.memory_create_relation_tool,
            "memory_search": self.memory_search_tool,
            "memory_add_observations": self.memory_add_observations_tool,

            # Context7 tools
            "context7_resolve_library": self.context7_resolve_library_tool,
            "context7_get_docs": self.context7_get_docs_tool,

            # Web search tools
            "search_web": self.search_web_tool,
            "web_search_prime": self.web_search_prime_tool,
            "web_fetch": self.web_fetch_tool,

            # Vision tools
            "analyze_image": self.analyze_image_tool,
            "analyze_video": self.analyze_video_tool,

            # Browser automation tools
            "navigate_to_url": self.navigate_to_url_tool,
            "take_screenshot": self.take_screenshot_tool,
            "click_element": self.click_element_tool,
            "fill_input": self.fill_input_tool,
            "browser_navigate": self.navigate_to_url_tool,  # Alias
            "browser_screenshot": self.take_screenshot_tool,  # Alias
            "browser_click": self.click_element_tool,  # Alias
            "browser_fill": self.fill_input_tool,  # Alias
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

    async def search_web_tool(self, query: str, count: int = 10) -> str:
        """Web search MCP tool: Search the web."""
        result = await self.web_search_integration.search_web_prime(query, count)
        if result.get("success"):
            search_results = result.get("results", [])
            if search_results:
                response = f"🔍 Found {len(search_results)} web results for '{query}':\n\n"
                for i, result in enumerate(search_results[:5], 1):
                    title = result.get('webPageTitle', 'No title')
                    url = result.get('webPageUrl', 'No URL')
                    snippet = result.get('webPageSummary', 'No summary')[:200]
                    response += f"{i}. **{title}**\n   URL: {url}\n   Summary: {snippet}...\n\n"
                return response
            return f"🔍 No results found for '{query}'"
        return f"❌ Web search failed: {result.get('error')}"

    async def web_search_prime_tool(self, query: str, count: int = 10, search_recency_filter: str = "noLimit") -> str:
        """WebSearchPrime MCP tool: Advanced web search."""
        result = await self.web_search_integration.search_web_prime(query, count, search_recency_filter)
        if result.get("success"):
            search_results = result.get("results", [])
            if search_results:
                response = f"🚀 Advanced search found {len(search_results)} results for '{query}':\n\n"
                for i, result in enumerate(search_results[:5], 1):
                    title = result.get('webPageTitle', 'No title')
                    url = result.get('webPageUrl', 'No URL')
                    snippet = result.get('webPageSummary', 'No summary')[:200]
                    site_name = result.get('websiteName', 'Unknown site')
                    response += f"{i}. **{title}** ({site_name})\n   URL: {url}\n   Summary: {snippet}...\n\n"
                return response
            return f"🚀 No results found for '{query}'"
        return f"❌ Advanced web search failed: {result.get('error')}"

    async def web_fetch_tool(self, url: str, return_format: str = "markdown") -> str:
        """Web fetch MCP tool: Read and convert web content."""
        result = await self.web_search_integration.web_reader(url, return_format)
        if result.get("success"):
            content = result.get("content", "")
            if content:
                return f"📄 Successfully fetched content from {url}:\n\n{content[:1000]}..." if len(content) > 1000 else f"📄 Successfully fetched content from {url}:\n\n{content}"
            return f"📄 No content found at {url}"
        return f"❌ Failed to fetch {url}: {result.get('error')}"

    async def analyze_image_tool(self, image_source: str, prompt: str) -> str:
        """Vision MCP tool: Analyze an image."""
        result = await self.vision_integration.analyze_image(image_source, prompt)
        if result.get("success"):
            analysis = result.get("analysis", "")
            return f"🖼️ Image analysis completed:\n\n{analysis}"
        return f"❌ Image analysis failed: {result.get('error')}"

    async def analyze_video_tool(self, video_source: str, prompt: str) -> str:
        """Vision MCP tool: Analyze a video."""
        result = await self.vision_integration.analyze_video(video_source, prompt)
        if result.get("success"):
            analysis = result.get("analysis", "")
            return f"🎥 Video analysis completed:\n\n{analysis}"
        return f"❌ Video analysis failed: {result.get('error')}"

    async def navigate_to_url_tool(self, url: str, browser_type: str = "chromium") -> str:
        """Browser automation MCP tool: Navigate to URL."""
        result = await self.browser_automation_integration.navigate_to_url(url, browser_type)
        if result.get("success"):
            return f"🌐 Successfully navigated to {url} using {browser_type}"
        return f"❌ Navigation failed: {result.get('error')}"

    async def take_screenshot_tool(self, name: str, full_page: bool = False) -> str:
        """Browser automation MCP tool: Take screenshot."""
        result = await self.browser_automation_integration.take_screenshot(name, full_page)
        if result.get("success"):
            page_type = "full page" if full_page else "viewport"
            return f"📸 Screenshot '{name}' taken successfully ({page_type})"
        return f"❌ Screenshot failed: {result.get('error')}"

    async def click_element_tool(self, selector: str) -> str:
        """Browser automation MCP tool: Click element."""
        result = await self.browser_automation_integration.click_element(selector)
        if result.get("success"):
            return f"🖱️ Successfully clicked element: {selector}"
        return f"❌ Click failed: {result.get('error')}"

    async def fill_input_tool(self, selector: str, value: str) -> str:
        """Browser automation MCP tool: Fill input field."""
        result = await self.browser_automation_integration.fill_input(selector, value)
        if result.get("success"):
            return f"⌨️ Successfully filled input {selector} with value length: {len(value)}"
        return f"❌ Fill input failed: {result.get('error')}"

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

def get_mcp_tool_definitions() -> List[Dict[str, Any]]:
    """Get MCP tool definitions in the format expected by Claude Agent SDK."""
    mcp_integration = get_mcp_integration()
    tool_definitions = []

    # Memory tools
    tool_definitions.append({
        "name": "memory_create_entity",
        "description": "Create a new entity in the knowledge graph with observations",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name of the entity"},
                "entity_type": {"type": "string", "description": "Type of entity (person, concept, event, etc.)"},
                "observations": {"type": "array", "items": {"type": "string"}, "description": "List of observations about this entity"}
            },
            "required": ["name", "entity_type", "observations"]
        }
    })

    tool_definitions.append({
        "name": "memory_search",
        "description": "Search the knowledge graph for entities and information",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query for the knowledge graph"}
            },
            "required": ["query"]
        }
    })

    # Web search tools
    tool_definitions.append({
        "name": "search_web",
        "description": "Search the web for current information on any topic",
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "Search query"},
                "count": {"type": "integer", "description": "Number of results to return (default: 10)"}
            },
            "required": ["query"]
        }
    })

    tool_definitions.append({
        "name": "web_fetch",
        "description": "Read and convert web content from URLs to markdown",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to fetch content from"},
                "return_format": {"type": "string", "enum": ["markdown", "text"], "description": "Format to return content in (default: markdown)"}
            },
            "required": ["url"]
        }
    })

    # Vision tools
    tool_definitions.append({
        "name": "analyze_image",
        "description": "Analyze an image using AI vision capabilities",
        "input_schema": {
            "type": "object",
            "properties": {
                "image_source": {"type": "string", "description": "Path to image file or image URL"},
                "prompt": {"type": "string", "description": "What to analyze or look for in the image"}
            },
            "required": ["image_source", "prompt"]
        }
    })

    # Browser automation tools
    tool_definitions.append({
        "name": "navigate_to_url",
        "description": "Navigate to a website using browser automation",
        "input_schema": {
            "type": "object",
            "properties": {
                "url": {"type": "string", "description": "URL to navigate to"},
                "browser_type": {"type": "string", "enum": ["chromium", "firefox", "webkit"], "description": "Browser type (default: chromium)"}
            },
            "required": ["url"]
        }
    })

    tool_definitions.append({
        "name": "take_screenshot",
        "description": "Take a screenshot of the current web page",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name for the screenshot"},
                "full_page": {"type": "boolean", "description": "Whether to capture full page (default: false)"}
            },
            "required": ["name"]
        }
    })

    tool_definitions.append({
        "name": "click_element",
        "description": "Click an element on the web page",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for element to click"}
            },
            "required": ["selector"]
        }
    })

    tool_definitions.append({
        "name": "fill_input",
        "description": "Fill text into an input field",
        "input_schema": {
            "type": "object",
            "properties": {
                "selector": {"type": "string", "description": "CSS selector for input field"},
                "value": {"type": "string", "description": "Text to fill in the input field"}
            },
            "required": ["selector", "value"]
        }
    })

    return tool_definitions