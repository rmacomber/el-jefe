#!/usr/bin/env python3
"""
Playwright Web Researcher Agent
Provides web research capabilities using Playwright browser automation
"""

import asyncio
from playwright.async_api import async_playwright
from datetime import datetime
from typing import List, Dict, Any
import json
import re
from pathlib import Path


class PlaywrightWebResearcher:
    """Web researcher that uses Playwright for automated web research"""

    def __init__(self, workspace_path: Path):
        self.workspace_path = workspace_path
        self.outputs_dir = workspace_path / "web_research_outputs"
        self.outputs_dir.mkdir(exist_ok=True)

    async def research_topic(self, topic: str, max_sources: int = 5) -> Dict[str, Any]:
        """
        Research a topic using Playwright web automation

        Args:
            topic: Research topic/query
            max_sources: Maximum number of sources to analyze

        Returns:
            Dictionary containing research results
        """
        research_results = {
            "topic": topic,
            "timestamp": datetime.now().isoformat(),
            "sources_analyzed": 0,
            "findings": [],
            "content": [],
            "screenshots": [],
            "errors": []
        }

        # Research sources to try
        research_sources = [
            {"name": "Wikipedia", "url": f"https://en.wikipedia.org/wiki/{topic.replace(' ', '_')}", "type": "encyclopedia"},
            {"name": "Google Search", "url": f"https://www.google.com/search?q={topic.replace(' ', '+')}", "type": "search"},
            {"name": "TechCrunch", "url": "https://techcrunch.com", "type": "tech_news"},
            {"name": "arXiv", "url": f"https://arxiv.org/search/?query={topic.replace(' ', '+')}&searchtype=all", "type": "academic"},
            {"name": "MIT Technology Review", "url": f"https://www.technologyreview.com/topic/{topic.lower().replace(' ', '-')}/", "type": "tech_analysis"}
        ]

        print(f"🔍 Starting web research on: {topic}")

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()

            try:
                for i, source in enumerate(research_sources[:max_sources]):
                    print(f"\n{i+1}. Researching: {source['name']} ({source['type']})")

                    try:
                        # Navigate to source
                        await page.goto(source['url'], timeout=30000)
                        await page.wait_for_load_state("networkidle", timeout=15000)

                        # Get page information
                        title = await page.title()
                        url = page.url

                        # Take screenshot
                        screenshot_name = f"research_{i+1}_{source['name'].lower().replace(' ', '_')}.png"
                        screenshot_path = self.outputs_dir / screenshot_name
                        await page.screenshot(path=str(screenshot_path))
                        research_results["screenshots"].append(screenshot_name)

                        # Extract content
                        content = await self._extract_content(page, source['type'])

                        research_results["sources_analyzed"] += 1
                        research_results["content"].append({
                            "source": source['name'],
                            "type": source['type'],
                            "title": title,
                            "url": url,
                            "content": content,
                            "screenshot": screenshot_name
                        })

                        print(f"   ✅ Successfully extracted {len(content)} characters from {source['name']}")

                    except Exception as e:
                        error_msg = f"Failed to research {source['name']}: {str(e)}"
                        print(f"   ❌ {error_msg}")
                        research_results["errors"].append(error_msg)

                # Analyze findings
                research_results["findings"] = await self._analyze_findings(research_results["content"], topic)

            except Exception as e:
                research_results["errors"].append(f"Browser automation error: {str(e)}")
                print(f"❌ Browser automation error: {e}")

            finally:
                await browser.close()

        # Save research results
        await self._save_research_results(research_results)

        print(f"\n🎯 Research completed!")
        print(f"   📊 Sources analyzed: {research_results['sources_analyzed']}")
        print(f"   📝 Total content: {sum(len(c['content']) for c in research_results['content']):,} characters")
        print(f"   🖼️ Screenshots taken: {len(research_results['screenshots'])}")
        print(f"   📋 Key findings: {len(research_results['findings'])}")

        return research_results

    async def _extract_content(self, page, source_type: str) -> str:
        """Extract relevant content based on source type"""
        try:
            if source_type == "encyclopedia":
                # For Wikipedia, focus on main content
                content = await page.locator("#mw-content-text").inner_text()
                return self._clean_text(content)

            elif source_type == "search":
                # For search results, extract result snippets
                try:
                    # Look for search result containers
                    results = await page.locator("div.g, .g, [data-ved]").all()
                    all_text = []
                    for result in results[:10]:  # Limit to first 10 results
                        text = await result.inner_text()
                        if text and len(text) > 50:  # Only include substantial content
                            all_text.append(text)
                    return self._clean_text("\n".join(all_text))
                except:
                    # Fallback to full page content
                    content = await page.inner_text()
                    return self._clean_text(content[:5000])  # Limit size

            else:
                # For other sources, get main content
                content = await page.inner_text()
                return self._clean_text(content[:8000])  # Limit to reasonable size

        except Exception as e:
            print(f"⚠️ Error extracting content: {e}")
            return f"Error extracting content: {str(e)}"

    def _clean_text(self, text: str) -> str:
        """Clean and format extracted text"""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove common web navigation text
        navigation_patterns = [
            r'Skip to main content',
            r'Navigation',
            r'Menu',
            r'Search',
            r'Accept.*cookies',
            r'Privacy policy',
            r'Terms of service'
        ]
        for pattern in navigation_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)
        return text.strip()

    async def _analyze_findings(self, content_list: List[Dict], topic: str) -> List[str]:
        """Analyze research findings and generate insights"""
        findings = []
        all_content = " ".join([c['content'] for c in content_list])

        # Look for key information patterns
        if len(all_content) > 1000:
            findings.append(f"Comprehensive research conducted on '{topic}'")
            findings.append(f"Analyzed {len(content_list)} different sources")

        # Look for recent dates (2023-2024)
        recent_years = re.findall(r'\b(2023|2024)\b', all_content)
        if recent_years:
            findings.append(f"Found references to recent years: {', '.join(set(recent_years))}")

        # Look for key technologies or concepts
        topic_lower = topic.lower()
        if "ai" in topic_lower or "artificial intelligence" in topic_lower:
            ai_terms = ["machine learning", "deep learning", "neural network", "LLM", "GPT", "transformer"]
            found_terms = [term for term in ai_terms if term in all_content.lower()]
            if found_terms:
                findings.append(f"Key AI technologies mentioned: {', '.join(found_terms[:3])}")

        return findings[:5]  # Limit to top 5 findings

    async def _save_research_results(self, results: Dict[str, Any]):
        """Save research results to file"""
        output_file = self.outputs_dir / f"research_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import aiofiles
        async with aiofiles.open(output_file, 'w') as f:
            await f.write(json.dumps(results, indent=2))

        # Also save as markdown for readability
        md_file = self.outputs_dir / f"research_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        await self._save_markdown_summary(results, md_file)

    async def _save_markdown_summary(self, results: Dict[str, Any], output_file: Path):
        """Save research summary as markdown"""
        markdown_content = f"""# Web Research Summary: {results['topic']}

**Date:** {results['timestamp']}
**Sources Analyzed:** {results['sources_analyzed']}

## Key Findings

"""

        for finding in results['findings']:
            markdown_content += f"• {finding}\n"

        markdown_content += f"""

## Sources Analyzed

"""

        for i, source in enumerate(results['content'], 1):
            markdown_content += f"""
### {i}. {source['source']} ({source['type']})

**Title:** {source['title'][:100]}
**URL:** {source['url']}
**Content Length:** {len(source['content'])} characters

"""
            if source['content']:
                preview = source['content'][:300] + "..." if len(source['content']) > 300 else source['content']
                markdown_content += f"**Preview:** {preview}\n\n"

        if results['errors']:
            markdown_content += f"""
## Errors Encountered

"""
            for error in results['errors']:
                markdown_content += f"• {error}\n"

        markdown_content += f"""
## Screenshots

Generated {len(results['screenshots'])} screenshots for visual verification.
"""

        import aiofiles
        async with aiofiles.open(output_file, 'w') as f:
            await f.write(markdown_content)


async def main():
    """Test the Playwright web researcher"""
    from pathlib import Path

    workspace = Path("test_web_research")
    workspace.mkdir(exist_ok=True)

    researcher = PlaywrightWebResearcher(workspace)

    # Test with a research topic
    results = await researcher.research_topic("AI machine learning breakthroughs 2024", max_sources=3)

    return results


if __name__ == "__main__":
    asyncio.run(main())