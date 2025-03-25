import json
import os
from typing import Any, Dict, List, Literal, Optional, Union

import requests
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions.kernel_arguments import KernelArguments

try:
    from tavily import TavilyClient
except ImportError:
    raise ImportError(
        "`tavily-python` not installed. Please install using `pip install tavily-python`"
    )


class TavilySearchPlugin:
    """Tool for searching the web with Tavily Search API"""

    def __init__(
        self,
        api_key: Optional[str] = None,
        search_mode: Literal["detailed", "context"] = "detailed",
        max_tokens: int = 6000,
        include_answer: bool = True,
        search_depth: Literal["basic", "advanced"] = "advanced",
        format: Literal["json", "markdown"] = "markdown",
        max_results: int = 5,
    ):
        """
        Initialize the Tavily search tool.

        Args:
            api_key: Tavily API key (defaults to TAVILY_API_KEY environment variable)
            search_mode: Use "detailed" for structured results or "context" for raw search context
            max_tokens: Maximum tokens in response
            include_answer: Whether to include AI-generated answer summary
            search_depth: Search depth ("basic" or "advanced")
            format: Response format ("json" or "markdown")
            max_results: Maximum number of results to return in detailed mode
        """
        # Initialize basic properties
        self._name = "tavily_search"
        self._search_mode = search_mode

        # Initialize API client
        self.api_key = api_key or os.getenv("TAVILY_API_KEY")
        if not self.api_key:
            raise ValueError("TAVILY_API_KEY not provided")
        self.client = TavilyClient(api_key=self.api_key)

        # Store configuration options
        self.search_depth = search_depth
        self.max_tokens = max_tokens
        self.include_answer = include_answer
        self.format = format
        self.max_results = max_results

    @property
    def name(self) -> str:
        """Get the name of the tool"""
        return self._name

    @property
    def description(self) -> str:
        """Get the description of the tool"""
        if self._search_mode == "detailed":
            return "Search the web for information and return structured results"
        else:
            return "Search the web for information and return raw context"

    @property
    def input_schema(self) -> Dict[str, Any]:
        """Get the input schema for the tool"""
        if self._search_mode == "detailed":
            return {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web",
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of results to return (optional)",
                    },
                },
                "required": ["query"],
            }
        else:
            return {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The search query to look up on the web",
                    }
                },
                "required": ["query"],
            }

    @kernel_function(
        description="Search for information on the web with Tavily API",
        name="web_search",
    )
    def search(self, query: str) -> str:
        """
        Search for information on the web with Tavily.

        Args:
            query: The search query to use.

        Returns:
            The search results.
        """
        client = TavilyClient(api_key=self.api_key)
        response = client.search(
            query=query,
            search_depth=self.search_depth,
            include_answer=self.include_answer,
            include_images=False,
            max_tokens=self.max_tokens,
            search_mode=self._search_mode,
        )

        if self.format == "json":
            return json.dumps(response)
        else:
            markdown = "# Search Results\n\n"
            if "answer" in response and response["answer"]:
                markdown += f"## Answer\n\n{response['answer']}\n\n"

            markdown += "## Sources\n\n"
            for i, result in enumerate(response.get("results", [])[: self.max_results]):
                title = result.get("title", "No Title")
                url = result.get("url", "")
                content = result.get("content", "No Content")
                markdown += f"{i+1}. **[{title}]({url})**\n   {content}\n\n"

            return markdown

    def search_detailed(self, query: str, max_results: Optional[int] = None) -> str:
        """
        Search the web with detailed, structured results.

        Args:
            query: The search query
            max_results: Maximum number of results (overrides instance default if provided)

        Returns:
            Formatted search results as JSON or markdown
        """
        # Use provided max_results or fall back to instance default
        max_results = max_results or self.max_results

        # Perform search
        response = self.client.search(
            query=query,
            search_depth=self.search_depth,
            include_answer=self.include_answer,
            max_results=max_results,
        )

        # Format and return results
        return self._format_detailed_results(query, response)

    def search_context(self, query: str) -> str:
        """
        Search the web and return raw context information.

        Args:
            query: The search query

        Returns:
            Raw search context as a string
        """
        return self.client.get_search_context(
            query=query,
            search_depth=self.search_depth,
            max_tokens=self.max_tokens,
            include_answer=self.include_answer,
        )

    def _format_detailed_results(self, query: str, response: Dict[str, Any]) -> str:
        """
        Format the detailed search results based on the configured format.

        Args:
            query: The original search query
            response: The raw response from Tavily API

        Returns:
            Formatted results as JSON or markdown
        """
        # Extract and structure the relevant information
        clean_response: Dict[str, Any] = {"query": query}
        if "answer" in response and self.include_answer:
            clean_response["answer"] = response["answer"]

        # Process results with token limit
        clean_results = self._process_results_with_token_limit(
            response.get("results", [])
        )
        clean_response["results"] = clean_results

        # Format according to the specified output format
        if self.format == "json":
            return json.dumps(clean_response) if clean_response else "No results found."
        elif self.format == "markdown":
            return self._convert_to_markdown(query, clean_response)
        else:
            return json.dumps(clean_response)

    def _process_results_with_token_limit(
        self, results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Process results while respecting token limit.

        Args:
            results: List of raw result items

        Returns:
            List of processed result items within token limit
        """
        clean_results = []
        current_token_count = 0

        for result in results:
            clean_result = {
                "title": result["title"],
                "url": result["url"],
                "content": result["content"],
                "score": result.get("score", 0),
            }

            result_tokens = len(json.dumps(clean_result))
            if current_token_count + result_tokens > self.max_tokens:
                break

            current_token_count += result_tokens
            clean_results.append(clean_result)

        return clean_results

    def _convert_to_markdown(self, query: str, data: Dict[str, Any]) -> str:
        """
        Convert structured data to markdown format.

        Args:
            query: The original search query
            data: Structured search results

        Returns:
            Markdown formatted string
        """
        markdown = f"# Search Results: {query}\n\n"

        # Add summary if available
        if "answer" in data:
            markdown += "## Summary\n"
            markdown += f"{data['answer']}\n\n"

        # Add individual results
        if data["results"]:
            markdown += "## Sources\n\n"
            for idx, result in enumerate(data["results"], 1):
                markdown += f"### {idx}. [{result['title']}]({result['url']})\n"
                markdown += f"{result['content']}\n\n"
        else:
            markdown += "No results found."

        return markdown
