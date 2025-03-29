import json
import os
from typing import Dict, List, Optional

from semantic_kernel.functions import kernel_function

from semantic_kernel_plugins.logger import SKLogger

try:
    from serpapi import GoogleSearch
except ImportError:
    raise ImportError(
        "`serpapi` not installed. Please install using `pip install google-search-results`"
    )


class SerpApiWebSearchPlugin:
    def __init__(
        self,
        api_key: Optional[str] = None,
        engine: str = "google",
        num_results: int = 8,
        include_images: bool = False,
        include_videos: bool = False,
        include_news: bool = False,
        include_shopping: bool = False,
    ):
        self.api_key = api_key or os.getenv("SERPAPI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "SerpAPI API key is required. Provide it in the constructor or set SERPAPI_API_KEY environment variable."
            )

        self.engine = engine
        self.num_results = num_results
        self.include_images = include_images
        self.include_videos = include_videos
        self.include_news = include_news
        self.include_shopping = include_shopping
        self.logger = SKLogger()

    @kernel_function(
        description="Search the web using SerpApi",
        name="search",
    )
    def search(self, query: str) -> str:
        self.logger.info(f"Searching for: {query}")

        try:
            params = {
                "api_key": self.api_key,
                "engine": self.engine,
                "q": query,
                "num": self.num_results,
            }

            search = GoogleSearch(params)
            results = search.get_dict()

            print(f"API Response Keys: {list(results.keys())}")

            if "error" in results:
                self.logger.error(f"SerpApi Error: {results['error']}")
                return f"Search failed: {results['error']}"

            if "organic_results" in results:
                result_count = len(results["organic_results"])
                self.logger.info(f"Search completed with {result_count} results")
            else:
                self.logger.info("No organic results found")
                for key in results.keys():
                    if isinstance(results[key], list):
                        self.logger.info(f"Found {len(results[key])} {key}")

            return self._format_adaptive_results(results)

        except Exception as e:
            self.logger.error(f"Search error: {str(e)}")
            return f"Search failed: {str(e)}"

    def _format_adaptive_results(self, results: Dict) -> str:
        markdown = "## Search Results\n\n"

        if "search_metadata" in results:
            markdown += f"*API: {results['search_metadata'].get('serpapi_version', 'Unknown')}*\n"
            markdown += (
                f"*Engine: {results['search_metadata'].get('engine', 'Unknown')}*\n\n"
            )

        if "organic_results" in results and results["organic_results"]:
            markdown += "### Web Results\n\n"
            for i, result in enumerate(results["organic_results"], 1):
                title = result.get("title", "No Title")
                link = result.get("link", "#")
                snippet = result.get("snippet", "No description available")

                markdown += f"{i}. **{title}**\n"
                markdown += f"{snippet}\n"
                markdown += f"[Link]({link})\n\n"

        if "news_results" in results and results["news_results"]:
            markdown += "### News Results\n\n"
            for i, result in enumerate(results["news_results"], 1):
                title = result.get("title", "No Title")
                link = result.get("link", "#")
                snippet = result.get("snippet", "No description available")
                source = result.get("source", "Unknown")

                markdown += f"{i}. **{title}** - *{source}*\n"
                markdown += f"{snippet}\n"
                markdown += f"[Link]({link})\n\n"

        if "shopping_results" in results and results["shopping_results"]:
            markdown += "### Shopping Results\n\n"
            for i, result in enumerate(results["shopping_results"], 1):
                title = result.get("title", "No Title")
                link = result.get("link", "#")
                price = result.get("price", "Price not available")

                markdown += f"{i}. **{title}** - {price}\n"
                markdown += f"[Link]({link})\n\n"

        if (
            not "organic_results" in results
            and not "news_results" in results
            and not "shopping_results" in results
        ):
            markdown += "### Raw Results\n\n"
            markdown += "No standard results found. The search returned the following categories:\n\n"

            important_keys = [k for k in results.keys() if not k.startswith("search_")]

            for key in important_keys:
                if isinstance(results[key], list) and len(results[key]) > 0:
                    markdown += f"- **{key}** ({len(results[key])} items)\n"

            for key in important_keys:
                if isinstance(results[key], list) and len(results[key]) > 0:
                    markdown += f"\n#### Sample {key}:\n"
                    sample = results[key][0]
                    if isinstance(sample, dict):
                        for sk, sv in sample.items():
                            if isinstance(
                                sv, (str, int, float, bool)
                            ) and not sk.startswith("_"):
                                markdown += f"- **{sk}**: {sv}\n"
                    break

        return markdown
