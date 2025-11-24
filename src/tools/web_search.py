"""
Web Search Tool

Provides web search capabilities for agents.
Can be implemented with various search APIs.
"""

import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
from datetime import datetime
import json


class WebSearchTool:
    """
    Web search tool for gathering information from the internet.
    Can work with different search providers.
    """

    def __init__(self, search_provider: str = "duckduckgo"):
        """
        Initialize the web search tool.

        Args:
            search_provider: The search provider to use (duckduckgo, google, bing, etc.)
        """
        self.search_provider = search_provider
        self.session = None

    async def search(
        self,
        query: str,
        max_results: int = 10,
        time_range: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform a web search.

        Args:
            query: Search query
            max_results: Maximum number of results to return
            time_range: Time range filter (e.g., "day", "week", "month", "year")

        Returns:
            List of search results
        """
        if self.search_provider == "duckduckgo":
            return await self._search_duckduckgo(query, max_results)
        elif self.search_provider == "custom":
            return await self._search_custom(query, max_results)
        else:
            # Fallback to mock results for demo
            return await self._mock_search(query, max_results)

    async def _search_duckduckgo(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Search using DuckDuckGo (instant answer API).

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of search results
        """
        url = "https://api.duckduckgo.com/"
        params = {
            "q": query,
            "format": "json",
            "no_html": 1,
            "skip_disambig": 1
        }

        if not self.session:
            self.session = aiohttp.ClientSession()

        try:
            async with self.session.get(url, params=params) as response:
                data = await response.json()

                results = []

                # Add instant answer if available
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", query),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data["Abstract"],
                        "source": "DuckDuckGo Instant Answer",
                        "timestamp": datetime.now().isoformat()
                    })

                # Add related topics
                for topic in data.get("RelatedTopics", [])[:max_results-len(results)]:
                    if "Text" in topic:
                        results.append({
                            "title": topic.get("FirstURL", "").split("/")[-1].replace("_", " "),
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic["Text"],
                            "source": "DuckDuckGo Related",
                            "timestamp": datetime.now().isoformat()
                        })

                return results[:max_results]

        except Exception as e:
            print(f"Search error: {e}")
            return await self._mock_search(query, max_results)

    async def _search_custom(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Custom search implementation (can be extended with APIs).

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            List of search results
        """
        # This is a placeholder for custom search implementation
        # You can integrate with:
        # - Google Custom Search API
        # - Bing Search API
        # - SerpAPI
        # - etc.

        return await self._mock_search(query, max_results)

    async def _mock_search(self, query: str, max_results: int) -> List[Dict[str, Any]]:
        """
        Mock search for testing/demonstration.

        Args:
            query: Search query
            max_results: Maximum results

        Returns:
            Mock search results
        """
        mock_results = [
            {
                "title": f"Mock result 1 for: {query}",
                "url": "https://example.com/result1",
                "snippet": f"This is a mock search result for the query '{query}'. In a real implementation, this would contain actual search results from the web.",
                "source": "Mock Search Engine",
                "timestamp": datetime.now().isoformat()
            },
            {
                "title": f"Mock result 2 for: {query}",
                "url": "https://example.com/result2",
                "snippet": f"Another mock result demonstrating how search results would be structured. Results can include various types of content from different sources.",
                "source": "Mock Search Engine",
                "timestamp": datetime.now().isoformat()
            }
        ]

        return mock_results[:max_results]

    async def summarize_results(self, results: List[Dict[str, Any]]) -> str:
        """
        Summarize search results into a coherent text.

        Args:
            results: List of search results

        Returns:
            Summarized text
        """
        if not results:
            return "No search results found."

        summary_parts = [f"Found {len(results)} search results:\n"]

        for i, result in enumerate(results, 1):
            summary_parts.append(
                f"{i}. {result['title']}\n"
                f"   URL: {result['url']}\n"
                f"   Summary: {result['snippet'][:200]}...\n"
            )

        return "\n".join(summary_parts)

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()