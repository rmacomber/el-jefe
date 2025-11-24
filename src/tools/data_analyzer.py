"""
Data Analyzer Tool

Provides data analysis capabilities for agents.
Can analyze structured data, identify patterns, and generate insights.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from datetime import datetime
from collections import Counter, defaultdict
import re


class DataAnalyzerTool:
    """
    Tool for analyzing data and generating insights.
    Works with JSON, CSV, and structured text data.
    """

    def __init__(self):
        """Initialize the data analyzer."""
        self.numeric_pattern = re.compile(r'-?\d+\.?\d*')

    async def analyze_json_data(self, data: Union[Dict, List]) -> Dict[str, Any]:
        """
        Analyze JSON data structure and content.

        Args:
            data: JSON data to analyze

        Returns:
            Analysis results
        """
        analysis = {
            "data_type": type(data).__name__,
            "analysis_timestamp": datetime.now().isoformat(),
            "structure": {},
            "statistics": {},
            "insights": []
        }

        if isinstance(data, dict):
            analysis["structure"] = await self._analyze_dict_structure(data)
            analysis["statistics"] = await self._analyze_dict_content(data)
        elif isinstance(data, list):
            analysis["structure"] = await self._analyze_list_structure(data)
            analysis["statistics"] = await self._analyze_list_content(data)
        else:
            analysis["insights"].append(f"Data is a simple {type(data).__name__}")

        return analysis

    async def analyze_text_data(self, text: str) -> Dict[str, Any]:
        """
        Analyze text data for patterns and insights.

        Args:
            text: Text to analyze

        Returns:
            Analysis results
        """
        lines = text.split('\n')
        words = text.split()
        sentences = [s.strip() for s in text.split('.') if s.strip()]

        analysis = {
            "text_statistics": {
                "character_count": len(text),
                "word_count": len(words),
                "line_count": len(lines),
                "sentence_count": len(sentences),
                "avg_words_per_sentence": len(words) / len(sentences) if sentences else 0
            },
            "patterns": {},
            "insights": [],
            "analysis_timestamp": datetime.now().isoformat()
        }

        # Find numeric values
        numbers = self._extract_numbers(text)
        if numbers:
            analysis["numeric_values"] = {
                "count": len(numbers),
                "values": numbers[:10],  # Show first 10
                "min": min(numbers),
                "max": max(numbers),
                "avg": sum(numbers) / len(numbers)
            }

        # Find common words
        word_freq = Counter(word.lower().strip('.,!?;:"()[]') for word in words)
        common_words = word_freq.most_common(10)
        if common_words:
            analysis["common_words"] = [{"word": w, "count": c} for w, c in common_words]

        # Detect patterns
        if self._contains_urls(text):
            analysis["patterns"]["contains_urls"] = True

        if self._contains_emails(text):
            analysis["patterns"]["contains_emails"] = True

        if self._contains_dates(text):
            analysis["patterns"]["contains_dates"] = True

        # Generate insights
        if analysis["text_statistics"]["word_count"] > 1000:
            analysis["insights"].append("This is a long text document")

        if analysis["text_statistics"]["avg_words_per_sentence"] > 20:
            analysis["insights"].append("Sentences are quite complex (high word count)")

        return analysis

    async def compare_data_sets(
        self,
        data1: Union[Dict, List],
        data2: Union[Dict, List],
        labels: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare two data sets.

        Args:
            data1: First data set
            data2: Second data set
            labels: Optional labels for the data sets

        Returns:
            Comparison analysis
        """
        if not labels:
            labels = ["Dataset 1", "Dataset 2"]

        analysis = {
            "comparison_timestamp": datetime.now().isoformat(),
            "datasets": labels,
            "similarity_metrics": {},
            "differences": [],
            "summary": ""
        }

        # Basic comparison
        type_match = type(data1) == type(data2)
        analysis["similarity_metrics"]["same_type"] = type_match

        if isinstance(data1, dict) and isinstance(data2, dict):
            await self._compare_dicts(data1, data2, analysis, labels)
        elif isinstance(data1, list) and isinstance(data2, list):
            await self._compare_lists(data1, data2, analysis, labels)
        else:
            analysis["differences"] = [
                f"Different data types: {type(data1).__name__} vs {type(data2).__name__}"
            ]

        return analysis

    async def identify_trends(
        self,
        data: List[Dict[str, Any]],
        date_field: str = "date",
        value_field: str = "value"
    ) -> Dict[str, Any]:
        """
        Identify trends in time-series or sequential data.

        Args:
            data: List of data points
            date_field: Field name for dates/timestamps
            value_field: Field name for values

        Returns:
            Trend analysis
        """
        if not data:
            return {"error": "No data provided"}

        analysis = {
            "analysis_timestamp": datetime.now().isoformat(),
            "data_points": len(data),
            "trends": {},
            "insights": []
        }

        try:
            # Extract values
            values = []
            for item in data:
                if value_field in item:
                    val = item[value_field]
                    if isinstance(val, (int, float)):
                        values.append(val)

            if len(values) < 2:
                analysis["insights"].append("Not enough numeric data for trend analysis")
                return analysis

            # Basic trend analysis
            first_half = values[:len(values)//2]
            second_half = values[len(values)//2:]

            first_avg = sum(first_half) / len(first_half)
            second_avg = sum(second_half) / len(second_half)

            if second_avg > first_avg * 1.1:
                analysis["trends"]["direction"] = "increasing"
                analysis["trends"]["strength"] = (second_avg - first_avg) / first_avg
            elif second_avg < first_avg * 0.9:
                analysis["trends"]["direction"] = "decreasing"
                analysis["trends"]["strength"] = (first_avg - second_avg) / first_avg
            else:
                analysis["trends"]["direction"] = "stable"
                analysis["trends"]["strength"] = 0

            # Statistics
            analysis["statistics"] = {
                "min": min(values),
                "max": max(values),
                "average": sum(values) / len(values),
                "total": sum(values)
            }

        except Exception as e:
            analysis["error"] = str(e)

        return analysis

    async def _analyze_dict_structure(self, data: Dict, depth: int = 0) -> Dict:
        """Analyze dictionary structure."""
        if depth > 5:  # Prevent infinite recursion
            return {"type": "dict", "depth_exceeded": True}

        structure = {
            "type": "dict",
            "key_count": len(data),
            "keys": list(data.keys())[:10],  # Show first 10 keys
            "key_types": {}
        }

        # Analyze key types
        for key, value in list(data.items())[:10]:
            if isinstance(value, dict):
                structure["key_types"][key] = await self._analyze_dict_structure(value, depth + 1)
            elif isinstance(value, list):
                structure["key_types"][key] = {
                    "type": "list",
                    "length": len(value)
                }
            else:
                structure["key_types"][key] = type(value).__name__

        return structure

    async def _analyze_list_structure(self, data: List) -> Dict:
        """Analyze list structure."""
        if not data:
            return {"type": "list", "length": 0}

        structure = {
            "type": "list",
            "length": len(data),
            "item_types": Counter(type(item).__name__ for item in data[:10])
        }

        # Show sample items
        structure["sample_items"] = str(data[:3])

        return structure

    async def _analyze_dict_content(self, data: Dict) -> Dict:
        """Analyze dictionary content for insights."""
        stats = {
            "nested_levels": 0,
            "numeric_values": 0,
            "string_values": 0,
            "list_values": 0,
            "dict_values": 0
        }

        for value in data.values():
            if isinstance(value, dict):
                stats["dict_values"] += 1
            elif isinstance(value, list):
                stats["list_values"] += 1
            elif isinstance(value, (int, float)):
                stats["numeric_values"] += 1
            elif isinstance(value, str):
                stats["string_values"] += 1

        return stats

    async def _analyze_list_content(self, data: List) -> Dict:
        """Analyze list content for insights."""
        stats = {
            "item_types": Counter(type(item).__name__ for item in data),
            "unique_items": len(set(str(item) for item in data)),
            "numeric_items": sum(1 for item in data if isinstance(item, (int, float))),
            "string_items": sum(1 for item in data if isinstance(item, str))
        }

        return stats

    async def _compare_dicts(
        self,
        dict1: Dict,
        dict2: Dict,
        analysis: Dict,
        labels: List[str]
    ):
        """Compare two dictionaries."""
        keys1 = set(dict1.keys())
        keys2 = set(dict2.keys())

        common_keys = keys1 & keys2
        unique_to_1 = keys1 - keys2
        unique_to_2 = keys2 - keys1

        analysis["similarity_metrics"]["common_keys"] = len(common_keys)
        analysis["similarity_metrics"]["unique_to_first"] = len(unique_to_1)
        analysis["similarity_metrics"]["unique_to_second"] = len(unique_to_2)

        if unique_to_1:
            analysis["differences"].append(
                f"Keys only in {labels[0]}: {', '.join(list(unique_to_1)[:5])}"
            )

        if unique_to_2:
            analysis["differences"].append(
                f"Keys only in {labels[1]}: {', '.join(list(unique_to_2)[:5])}"
            )

        # Compare values for common keys
        value_differences = 0
        for key in common_keys:
            if dict1[key] != dict2[key]:
                value_differences += 1

        if common_keys:
            analysis["similarity_metrics"]["value_similarity"] = (
                (len(common_keys) - value_differences) / len(common_keys)
            )

    async def _compare_lists(
        self,
        list1: List,
        list2: List,
        analysis: Dict,
        labels: List[str]
    ):
        """Compare two lists."""
        analysis["similarity_metrics"]["length_difference"] = abs(len(list1) - len(list2))

        # Compare as sets for content similarity
        set1 = set(str(item) for item in list1)
        set2 = set(str(item) for item in list2)

        common = set1 & set2
        analysis["similarity_metrics"]["common_items"] = len(common)

        if set1 or set2:
            analysis["similarity_metrics"]["content_similarity"] = (
                len(common) / len(set1 | set2)
            )

    def _extract_numbers(self, text: str) -> List[float]:
        """Extract all numeric values from text."""
        numbers = []
        for match in self.numeric_pattern.finditer(text):
            try:
                numbers.append(float(match.group()))
            except ValueError:
                pass
        return numbers

    def _contains_urls(self, text: str) -> bool:
        """Check if text contains URLs."""
        url_pattern = re.compile(r'https?://[^\s]+')
        return bool(url_pattern.search(text))

    def _contains_emails(self, text: str) -> bool:
        """Check if text contains email addresses."""
        email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        return bool(email_pattern.search(text))

    def _contains_dates(self, text: str) -> bool:
        """Check if text contains dates."""
        date_pattern = re.compile(r'\b\d{1,4}[/-]\d{1,2}[/-]\d{1,4}\b')
        return bool(date_pattern.search(text))