# Semantic Kernel Plugins

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)

A collection of ready-to-use plugins for Microsoft's Semantic Kernel framework that enhances AI applications with database connectivity, shell operations, web search capabilities, Python code execution, and detailed logging.

## 🚀 Overview

Semantic Kernel Plugins provides a set of powerful, production-ready plugins for the Semantic Kernel Framework, eliminating the need to write your own plugins from scratch:

* **PostgreSQL Plugin**: Connect and interact with PostgreSQL databases
* **Shell Plugin**: Execute system commands across different operating systems
* **Web Search Plugin**: Integrate Tavily search API for web search capabilities
* **Python Code Generator**: Generate and execute Python code safely

## ✨ Features

* **Database Integration**: Execute queries, fetch data, and manage PostgreSQL databases
* **System Command Execution**: Run shell commands with proper handling for Windows, Linux, and macOS
* **Web Search Integration**: Search the web using Tavily API with rich result formatting
* **Python Code Generation and Execution**: Generate and execute Python code in a controlled environment
* **Enhanced Logging**: Track operations with detailed, colorful logs
* **Cross-Platform Compatibility**: Works seamlessly across Windows, Linux, and macOS

## 📋 Requirements

* Python 3.10+
* Semantic Kernel 1.0.0+

## 📥 Installation

```bash
pip install semantic-kernel-plugins
```

## 🚀 Quick Start

### PostgreSQL Plugin

```python
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from psycopg2 import connect
from semantic_kernel_plugins.plugins.postgre import PostgrePlugin

# Initialize connection
db_connection = connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD")
)

# Create kernel and add plugin
kernel = Kernel()
kernel.add_plugin(
    PostgrePlugin(db_connection),
    plugin_name="PostgreSQL"
)

# Now you can use the plugin in your AI workflows
# Example: kernel.plugins["PostgreSQL"].execute_query("SELECT * FROM users")
```

### Shell Plugin

```python
from semantic_kernel import Kernel
from semantic_kernel_plugins.plugins.shell import ShellPlugin

# Create kernel and add shell plugin
kernel = Kernel()
kernel.add_plugin(
    ShellPlugin(),
    plugin_name="Shell"
)

# Now you can execute shell commands
# Example: kernel.plugins["Shell"].execute_shell_command("ls -la")
```

### Web Search Plugin

```python
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel_plugins.plugins.web.tavily_web_search import TavilySearchPlugin
from semantic_kernel_plugins.logger.sk_logger import SKLogger

# Setup logger
logger = SKLogger(name="MyApp")

# Create kernel and add web search plugin
kernel = Kernel()
kernel.add_plugin(
    TavilySearchPlugin(
        api_key=os.getenv("TAVILY_API_KEY"),
        logger=logger
    ),
    plugin_name="WebSearch"
)

# Now you can search the web
# Example: kernel.plugins["WebSearch"].search("latest developments in AI")
```

## 📦 Available Plugins

| Plugin | Description |
|--------|-------------|
| PostgrePlugin | Interact with PostgreSQL databases |
| ShellPlugin | Execute shell commands across different platforms |
| TavilySearchPlugin | Search the web using Tavily API |
| PythonCodeGeneratorPlugin | Generate and execute Python code |
| CalculatorPlugin | Perform mathematical calculations |

## 🔜 Coming Soon

* .NET Plugins
* MongoDB Plugin
* SQLite Plugin
* File System Plugin
* More Cloud Service Integrations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ for AI developers working with Microsoft's Semantic Kernel.
