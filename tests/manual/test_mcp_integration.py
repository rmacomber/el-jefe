#!/usr/bin/env python3
"""
Test MCP Integration with El Jefe

Tests the Memory MCP and Context7 MCP server integration.
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, "src")


async def test_memory_mcp():
    """Test Memory MCP integration."""
    print("🧪 Testing Memory MCP Integration...")

    try:
        from mcp_integration import get_mcp_integration
        mcp = get_mcp_integration()

        # Test creating an entity
        result = await mcp.execute_tool(
            "memory_create_entity",
            name="Python Programming",
            entity_type="technology",
            observations=["Python is a high-level programming language", "Created by Guido van Rossum"]
        )
        print(f"Entity creation: {result}")

        # Test searching
        result = await mcp.execute_tool(
            "memory_search",
            query="Python"
        )
        print(f"Search result: {result}")

        return True

    except Exception as e:
        print(f"❌ Memory MCP test failed: {e}")
        return False


async def test_context7_mcp():
    """Test Context7 MCP integration."""
    print("\n🧪 Testing Context7 MCP Integration...")

    try:
        from mcp_integration import get_mcp_integration
        mcp = get_mcp_integration()

        # Test resolving a library
        result = await mcp.execute_tool(
            "context7_resolve_library",
            library_name="react"
        )
        print(f"Library resolution: {result}")

        return True

    except Exception as e:
        print(f"❌ Context7 MCP test failed: {e}")
        return False


async def test_el_jefe_with_mcp():
    """Test El Jefe with MCP integration."""
    print("\n🧪 Testing El Jefe Agent Manager with MCP...")

    try:
        from agent_manager import AgentConfig, AgentType

        # Test getting enhanced config
        config = AgentConfig.get_enhanced_config(AgentType.RESEARCHER)
        print(f"Enhanced researcher config tools: {config['allowed_tools'][:5]}...")  # Show first 5 tools

        # Check if MCP tools are in the list
        mcp_tools = [tool for tool in config['allowed_tools'] if tool.startswith(('memory_', 'context7_'))]
        print(f"MCP tools in config: {mcp_tools}")

        return len(mcp_tools) > 0

    except Exception as e:
        print(f"❌ El Jefe MCP test failed: {e}")
        return False


async def main():
    """Run all MCP integration tests."""
    print("🚀 MCP Integration Test Suite")
    print("=" * 50)

    # Test individual MCP servers
    memory_test = await test_memory_mcp()
    context7_test = await test_context7_mcp()
    el_jefe_test = await test_el_jefe_with_mcp()

    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"Memory MCP: {'✅ PASS' if memory_test else '❌ FAIL'}")
    print(f"Context7 MCP: {'✅ PASS' if context7_test else '❌ FAIL'}")
    print(f"El Jefe Integration: {'✅ PASS' if el_jefe_test else '❌ FAIL'}")

    all_passed = memory_test and context7_test and el_jefe_test

    if all_passed:
        print("\n🎉 All MCP integration tests passed!")
        print("✅ El Jefe agents now have access to Memory and Context7 MCP servers!")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")

    return all_passed


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)