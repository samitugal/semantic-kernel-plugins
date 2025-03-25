# Semantic Kernel Ready to Use Tools

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)

A collection of tools and plugins for Semantic Kernel Framework that enhances AI applications with Python code execution, web search capabilities, and detailed logging.

## 🚀 Overview

Semantic Kernel Tools provides a set of powerful plugins for the Semantic Kernel Framework:

* **Python Code Generator**: Generate and execute Python code safely based on natural language requests
* **Web Search Plugin**: Integrate Tavily search API for web search capabilities
* **SK Logger**: Enhanced logging with colorful output and detailed tracking

## ✨ Features

* **Python Code Generation and Execution**: Generate robust Python code and execute it in a controlled environment
* **Web Search Integration**: Search the web using Tavily API
* **Enhanced Logging**: Track AI operations with detailed, colorful logs
* **Extensible Architecture**: Easily customize or extend functionality

## 📋 Requirements

* Python 3.10+
* Semantic Kernel 1.0.0+

## 📥 Installation

```bash
pip install semantic-kernel-tools
```

## 🚀 Quick Start

```python
import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from dotenv import load_dotenv

from semantic_kernel_tools import SKLogger, LogLevel, PythonCodeGeneratorPlugin, TavilySearchPlugin

async def main():
    # Load environment variables
    load_dotenv()
    
    # Create a new kernel
    kernel = Kernel()
    
    # Add Bedrock service
    kernel.add_service(
        BedrockChatCompletion(model_id=os.getenv("ANTHROPIC_MODEL_ID"))
    )
    
    # Create logger
    logger = SKLogger(name="SKDemo", level=LogLevel.INFO)
    
    # Add Python Code Generator plugin
    python_generator = PythonCodeGeneratorPlugin()
    kernel.add_plugin(python_generator, plugin_name="PythonCodeGenerator")
    
    # Add Tavily Web Search plugin
    tavily_search = TavilySearchPlugin(api_key=os.getenv("TAVILY_API_KEY"))
    kernel.add_plugin(tavily_search, plugin_name="TavilyWebSearch")
    
    # Use the plugins
    code_request = "Create a function to calculate the factorial of a number and then compute 10!"
    search_request = "What are the latest developments in quantum computing?"
    
    logger.section("EXECUTING CODE")
    code_result = await python_generator.generate_and_execute_code(code_request)
    
    logger.section("WEB SEARCH")
    search_result = await tavily_search.search(search_request)
    
    print(code_result)
    print(search_result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

Built with ❤️ for AI developers working with Semantic Kernel.