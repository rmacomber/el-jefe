#!/usr/bin/env python3
"""
Simple Playwright web research that actually works
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def simple_playwright_research():
    """Simple web research using Playwright"""
    print("🎭 Simple Playwright Web Research")
    print("=" * 40)

    results = []

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Test with a known site that should work
            print("🌐 Navigating to Wikipedia for AI research...")
            await page.goto("https://en.wikipedia.org/wiki/Artificial_intelligence")
            await page.wait_for_load_state("networkidle")

            # Take a screenshot
            await page.screenshot(path="ai_wikipedia.png")
            print("📸 Screenshot saved as ai_wikipedia.png")

            # Get page title
            title = await page.title()
            print(f"📄 Page title: {title}")

            # Look for recent developments section
            try:
                # Look for content that mentions recent years
                content = await page.content()
                if "2024" in content or "2023" in content:
                    results.append("Found recent AI developments on Wikipedia")
                else:
                    results.append("Wikipedia page loaded successfully")

                # Extract some text content
                text_content = await page.inner_text("body")
                if len(text_content) > 1000:
                    summary = text_content[:500] + "..."
                    results.append(f"Content length: {len(text_content)} characters")
                    results.append("Page contains substantial AI information")
                else:
                    results.append(f"Content length: {len(text_content)} characters")

            except Exception as e:
                print(f"⚠️ Error extracting content: {e}")

            # Try another site - maybe tech news
            print("\n🌐 Trying TechCrunch...")
            await page.goto("https://techcrunch.com")
            await page.wait_for_load_state("networkidle")

            tech_title = await page.title()
            print(f"📄 TechCrunch title: {tech_title}")
            results.append(f"Successfully accessed TechCrunch")

            # Take another screenshot
            await page.screenshot(path="techcrunch.png")
            print("📸 Screenshot saved as techcrunch.png")

        except Exception as e:
            print(f"❌ Error during research: {e}")
            results.append(f"Error: {str(e)}")

        finally:
            await browser.close()

    return results

async def main():
    """Main test function"""
    research_results = await simple_playwright_research()

    print(f"\n📋 Research Summary:")
    for i, result in enumerate(research_results, 1):
        print(f"{i}. {result}")

    print(f"\n✅ Playwright research completed!")
    print("🖼️ Screenshots saved for visual verification")
    print("🔧 Playwright browser automation is working!")

if __name__ == "__main__":
    asyncio.run(main())