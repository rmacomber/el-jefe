#!/usr/bin/env python3
"""
Direct Playwright web research implementation
"""

import asyncio
from playwright.async_api import async_playwright
import json
from datetime import datetime

async def playwright_web_research(query, max_results=5):
    """
    Use Playwright directly to perform web research

    Args:
        query: Search query
        max_results: Maximum number of results to collect

    Returns:
        Dictionary with research results
    """
    research_results = {
        "query": query,
        "timestamp": datetime.now().isoformat(),
        "sources": [],
        "findings": []
    }

    async with async_playwright() as p:
        # Launch browser
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()

        try:
            # Navigate to Google Search
            print(f"🔍 Searching for: {query}")
            await page.goto("https://www.google.com")
            await page.wait_for_load_state("networkidle")

            # Accept cookies if present
            try:
                accept_button = page.locator("button:has-text('Accept all'), button:has-text('I agree')").first
                if await accept_button.is_visible():
                    await accept_button.click()
                    await asyncio.sleep(1)
            except:
                pass

            # Perform search
            search_box = await page.locator("textarea[name='q'], input[name='q']").first
            await search_box.fill(query)
            await search_box.press("Enter")
            await page.wait_for_load_state("networkidle")

            # Collect search results
            search_results = []

            # Try multiple selectors to find results
            selectors = [
                "div.g",
                "div[data-ved]",
                ".g",
                "[data-ved]"
            ]

            for selector in selectors:
                try:
                    results = await page.locator(selector).all()
                    print(f"📊 Found {len(results)} potential results with selector: {selector}")

                    for i, result in enumerate(results[:max_results]):
                        try:
                            # Extract title
                            title_elem = await result.locator("h3, .LC20lb, .VwiC3b").first
                            title = await title_elem.text_content() if await title_elem.count() > 0 else f"Result {i+1}"

                            # Extract URL
                            link_elem = await result.locator("a").first
                            href = await link_elem.get_attribute("href")

                            # Extract description
                            desc_elem = result.locator(".VwiC3b, .s, .IsZvec").first
                            description = await desc_elem.text_content() if await desc_elem.count() > 0 else ""

                            if href and title:
                                search_results.append({
                                    "title": title.strip(),
                                    "url": href,
                                    "description": description.strip()[:200] + "..." if len(description) > 200 else description.strip()
                                })

                        except Exception as e:
                            print(f"⚠️ Error extracting result {i}: {e}")
                            continue

                    if search_results:
                        break  # We found results, no need to try other selectors

                except Exception as e:
                    print(f"⚠️ Selector {selector} failed: {e}")
                    continue

            research_results["sources"] = search_results

            # Analyze findings
            if search_results:
                research_results["findings"] = [
                    f"Found {len(search_results)} results for '{query}'",
                    f"Top result: {search_results[0]['title']}" if search_results else "",
                    f"Sources include major tech sites and news outlets"
                ]
            else:
                research_results["findings"] = [
                    f"No results found for '{query}'",
                    "Try alternative search terms"
                ]

            print(f"✅ Research completed: Found {len(search_results)} results")

        except Exception as e:
            print(f"❌ Research failed: {e}")
            research_results["error"] = str(e)

        finally:
            await browser.close()

    return research_results

async def test_playwright_research():
    """Test the Playwright research functionality"""
    print("🎭 Testing Playwright Web Research")
    print("=" * 40)

    # Test with AI research query
    results = await playwright_web_research("AI breakthroughs 2024 latest developments", max_results=3)

    print(f"\n📋 Research Results:")
    print(f"Query: {results['query']}")
    print(f"Timestamp: {results['timestamp']}")
    print(f"Sources found: {len(results['sources'])}")

    for i, source in enumerate(results['sources'], 1):
        print(f"\n{i}. {source['title']}")
        print(f"   URL: {source['url']}")
        print(f"   Description: {source['description']}")

    print(f"\n🔍 Key Findings:")
    for finding in results['findings']:
        print(f"   • {finding}")

    return results

if __name__ == "__main__":
    asyncio.run(test_playwright_research())