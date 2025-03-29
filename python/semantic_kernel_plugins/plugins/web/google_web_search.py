import json
import os
from typing import Any, Dict, List, Literal, Optional, Union

import requests
from semantic_kernel.functions import kernel_function
from semantic_kernel_plugins.logger import SKLogger

try:
    from googlesearch import search
except ImportError:
    raise ImportError("`googlesearch-python` not installed. Please install using `pip install googlesearch-python`")

class GoogleSearchPlugin:
    def __init__(self, 
                max_results: Optional[int] = None,
                headers: Optional[Any] = None,
                proxy: Optional[str] = None,
                timeout: Optional[int] = 10,
                advanced: Optional[bool] = False,
            ):

        self.max_results: Optional[int] = max_results
        self.headers: Optional[Any] = headers
        self.proxy: Optional[str] = proxy
        self.timeout: Optional[int] = timeout
        self.advanced: Optional[bool] = advanced
        self.logger = SKLogger()

    @kernel_function(
        description="Search the web using Google",
        name="google_search",
    )
    def google_search(self, query: str) -> str:
        self.logger.info(f"Searching for: {query}")
        try:
            results = list(search(query, num_results=self.max_results, advanced=self.advanced))
            if not results:
                return "No results found."
            
            return self._format_results_markdown(results)
        except Exception as e:
            self.logger.error(f"Error searching: {e}")
            return f"Search failed: {str(e)}"

    def _format_results_markdown(self, results):
        if not results:
            return "No results found."
        
        output = "## Search Results\n\n"
        
        for idx, result in enumerate(results, 1):
            title = getattr(result, 'title', 'No title')
            url = getattr(result, 'url', 'No URL')
            description = getattr(result, 'description', 'No description available')
            
            output += f"### {idx}. {title}\n"
            output += f"URL: {url}\n"
            output += f"{description}\n\n"
        
        return output
