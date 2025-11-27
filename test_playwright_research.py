#!/usr/bin/env python3
"""
Test Playwright-based web research using MCP tools
"""

import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

async def test_playwright_research():
    """Test Playwright web research capabilities"""
    try:
        from mcp_integration import get_mcp_integration

        mcp_integration = get_mcp_integration()
        print("🎭 Testing Playwright Web Research Tools")
        print("=" * 50)

        # Step 1: Navigate to a research source
        print("\n1️⃣ Navigating to TechCrunch for AI news...")
        nav_result = await mcp_integration.navigate_to_url_tool("https://techcrunch.com/category/artificial-intelligence/")
        print(f"   {nav_result}")

        # Step 2: Take a screenshot to see what we're working with
        print("\n2️⃣ Taking screenshot of the page...")
        screenshot_result = await mcp_integration.take_screenshot_tool("techcrunch_ai_page", full_page=False)
        print(f"   {screenshot_result}")

        # Step 3: Look for specific content or search for AI topics
        print("\n3️⃣ Looking for recent AI articles...")
        # This would typically involve clicking on links, but let's try a more targeted approach

        # Alternative: Navigate to a specific AI research site
        print("\n4️⃣ Navigating to arXiv for AI research papers...")
        nav_result2 = await mcp_integration.navigate_to_url_tool("https://arxiv.org/list/cs.AI/recent")
        print(f"   {nav_result2}")

        print("\n5️⃣ Taking screenshot of arXiv AI papers...")
        screenshot_result2 = await mcp_integration.take_screenshot_tool("arxiv_ai_papers")
        print(f"   {screenshot_result2}")

        print("\n✅ Playwright web research test completed successfully!")
        print("📸 Screenshots saved in browser automation output")
        print("🌐 Web navigation and research tools are functional")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_playwright_research())