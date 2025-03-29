# Semantic Kernel Plugins

![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue)
![License MIT](https://img.shields.io/badge/License-MIT-green)

A collection of ready-to-use plugins for Microsoft's Semantic Kernel framework that enhances AI applications with database connectivity, shell operations, web search capabilities, Python code execution, and detailed logging.

## 🚀 Overview

Semantic Kernel Plugins provides a set of powerful, production-ready plugins for the Semantic Kernel Framework, eliminating the need to write your own plugins from scratch:

* **PostgreSQL Plugin**: Connect and interact with PostgreSQL databases with ease
* **MongoDB Plugin**: Use MongoDB databases directly in your AI workflows
* **Shell Plugin**: Execute system commands safely across different operating systems
* **Web Search Plugins**: Choose from multiple search providers (Tavily, Google, SerpAPI)
* **Python Code Generator**: Generate and execute Python code safely

## ✨ Features

* **Multiple Database Integrations**: Connect to PostgreSQL and MongoDB databases
* **Cross-Platform Shell Operations**: Run system commands with proper handling for Windows, Linux, and macOS
* **Multi-Provider Web Search**: Choose from Tavily, Google Search, or SerpAPI for web searches
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

### Database Plugins

#### PostgreSQL Plugin

```python
import os
from dotenv import load_dotenv
from semantic_kernel import Kernel
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

# Example usage
# Execute SQL queries directly from your AI workflows
result = kernel.plugins["PostgreSQL"].execute_query("SELECT * FROM users")

# Get table schemas
tables = kernel.plugins["PostgreSQL"].fetch_table_names()
schema = kernel.plugins["PostgreSQL"].fetch_table_schema("users")
```

#### MongoDB Plugin

```python
from pymongo import MongoClient
from semantic_kernel import Kernel
from semantic_kernel_plugins.plugins.mongodb import MongoDBPlugin

# Initialize MongoDB client
client = MongoClient("mongodb://localhost:27017/")

# Create kernel and add plugin
kernel = Kernel()
kernel.add_plugin(
    MongoDBPlugin(client),
    plugin_name="MongoDB"
)

# Example usage
# Check if database exists
exists = kernel.plugins["MongoDB"].database_exists("mydatabase")

# List all collections in a database
collections = kernel.plugins["MongoDB"].list_collections("mydatabase")

# Get database statistics
stats = kernel.plugins["MongoDB"].get_database_stats("mydatabase")
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

# Execute shell commands safely across platforms
result = kernel.plugins["Shell"].execute_shell_command("ls -la")

# You can also pass a list of arguments
result = kernel.plugins["Shell"].execute_shell_command(["python", "-c", "print('Hello from Python!')"])
```

### Web Search Plugins

#### Tavily Search Plugin

```python
import os
from semantic_kernel import Kernel
from semantic_kernel_plugins.plugins.web.tavily_web_search import TavilySearchPlugin
from semantic_kernel_plugins.logger.sk_logger import SKLogger

# Setup logger for detailed search result tracking
logger = SKLogger(name="SearchApp")

# Create kernel and add web search plugin
kernel = Kernel()
kernel.add_plugin(
    TavilySearchPlugin(
        api_key=os.getenv("TAVILY_API_KEY"),
        search_depth="advanced",
        include_answer=True,
        logger=logger
    ),
    plugin_name="TavilySearch"
)

# Search the web with detailed results
results = kernel.plugins["TavilySearch"].search("latest advancements in quantum computing")
```

#### SerpAPI Search Plugin

```python
import os
from semantic_kernel import Kernel
from semantic_kernel_plugins.plugins.web import SerpApiWebSearchPlugin

# Create kernel and add SerpAPI search plugin
kernel = Kernel()
kernel.add_plugin(
    SerpApiWebSearchPlugin(
        api_key=os.getenv("SERPAPI_API_KEY"),
        engine="google",
        include_news=True  # Get additional news results
    ),
    plugin_name="SerpApiSearch"
)

# Search the web with Google via SerpAPI
results = kernel.plugins["SerpApiSearch"].search("current global economic trends")
```

#### Google Search Plugin

```python
from semantic_kernel import Kernel
from semantic_kernel_plugins.plugins.web import GoogleSearchPlugin

# Create kernel and add Google search plugin
kernel = Kernel()
kernel.add_plugin(
    GoogleSearchPlugin(
        max_results=10,
        advanced=True
    ),
    plugin_name="GoogleSearch"
)

# Search the web directly with Google
results = kernel.plugins["GoogleSearch"].google_search("best practices for cloud security")
```

## 📦 Available Plugins

| Plugin | Description |
|--------|-------------|
| **Database Plugins** |
| PostgrePlugin | Execute queries and manage PostgreSQL databases |
| MongoDBPlugin | Interact with MongoDB databases and collections |
| **System Plugins** |
| ShellPlugin | Execute shell commands across different platforms safely |
| **Web Search Plugins** |
| TavilySearchPlugin | AI-powered search with summarization via Tavily |
| SerpApiWebSearchPlugin | Comprehensive search results via SerpAPI (Google) |
| GoogleSearchPlugin | Direct Google search integration |
| **Development Plugins** |
| PythonCodeGeneratorPlugin | Generate and execute Python code safely |
| CalculatorPlugin | Perform mathematical calculations |

## 🔍 Detailed Plugin Features

### PostgreSQL Plugin
- Execute arbitrary SQL queries
- Fetch table names and schemas
- Insert, update, and delete data
- Create and drop tables

### MongoDB Plugin
- List databases and collections
- Check if databases or collections exist
- Get database and collection statistics

### Shell Plugin
- Cross-platform command execution
- Safe handling of command arguments
- Proper error reporting and logging

### Web Search Plugins
- Multiple search providers for different needs
- Configurable result formatting (markdown or JSON)
- Rich search results with titles, snippets, and URLs
- Advanced options for specialized searches (news, images, etc.)

## 🔜 Coming Soon

* .NET Plugins
* SQLite Plugin
* File System Plugin
* More Cloud Service Integrations

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

---

Built with ❤️ for AI developers working with Microsoft's Semantic Kernel.
