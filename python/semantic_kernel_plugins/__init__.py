"""
Semantic Kernel Plugins

A collection of ready-to-use tools and plugins for Semantic Kernel.
"""

__version__ = "0.1.0"

from semantic_kernel_plugins.plugins.calculator.calculator import \
    CalculatorPlugin
from semantic_kernel_plugins.plugins.python.python_code_generator import \
    PythonCodeGeneratorPlugin
from semantic_kernel_plugins.plugins.web.tavily_web_search import \
    TavilySearchPlugin

__all__ = [
    "PythonCodeGeneratorPlugin",
    "TavilySearchPlugin",
    "CalculatorPlugin",
]
