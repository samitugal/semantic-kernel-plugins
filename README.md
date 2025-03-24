# Python Executor Tool for Semantic Kernel

![Python Executor Tool](https://img.shields.io/badge/Semantic%20Kernel-Python%20Executor-blue)
![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-green)
![License MIT](https://img.shields.io/badge/License-MIT-yellow)

A powerful Python code execution tool for Semantic Kernel Framework that enables safe code generation, execution, and monitoring in AI applications.

## 🚀 Overview

Python Executor Tool is a Semantic Kernel plugin that allows your AI agents to:

- Generate Python code based on natural language requests
- Execute code safely in a controlled environment
- Monitor execution and handle errors gracefully
- Visualize the AI's thinking process with detailed logging

This tool bridges the gap between language models and Python execution, giving your AI applications the ability to solve complex computational problems and automate tasks through code.

## ✨ Features

- **Advanced Code Generation**: Analyzes user requests and generates robust, well-structured Python code
- **Secure Execution Environment**: Runs code in an isolated context with configurable security restrictions
- **Dependency Management**: Automatically detects and installs required packages
- **Error Handling**: Provides detailed error reports and recovery mechanisms
- **Colorful Logging**: Tracks the AI's thought process, planning, and execution results
- **Extensible Architecture**: Easily customize or extend functionality to meet your needs

## 📋 Requirements

- Python 3.13+
- [Semantic Kernel](https://github.com/microsoft/semantic-kernel) 1.25.0+
- Amazon Bedrock access (for Claude or other compatible models)

## 📥 Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/python-executor-tool.git
cd python-executor-tool

# Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Configuration

Create a `.env` file in the root directory with your API keys:

## 🚀 Quick Start

Here's a simple example of how to use the Python Executor Tool:

```python
import asyncio
import os
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from dotenv import load_dotenv

from src.plugins.python_code_generator import PythonCodeGeneratorPlugin
from src.plugins.sk_logger import SKLogger, LogLevel

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
    logger = SKLogger(name="PythonExecutorDemo", level=LogLevel.INFO)
    
    # Add Python Code Generator plugin
    python_generator = PythonCodeGeneratorPlugin(model_id=os.getenv("ANTHROPIC_MODEL_ID"))
    kernel.add_plugin(python_generator, plugin_name="PythonCodeGenerator")
    
    # Generate and execute Python code
    request = "Create a function to calculate the factorial of a number and then compute 10!"
    
    logger.section("EXECUTING CODE REQUEST")
    result = await python_generator.generate_and_execute_code(request)
    
    print("\n" + "="*50 + "\n")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
```

## 🔍 Core Components

### 1. PythonCodeGeneratorPlugin

This plugin handles code generation by interfacing with language models through Semantic Kernel:

```python
# Generate Python code
result = await python_generator.generate_python_code("Calculate the first 10 Fibonacci numbers")

# Generate and execute code in one step
result = await python_generator.generate_and_execute_code("Plot a sine wave using matplotlib")
```

### 2. ExecutePythonCodePlugin

Executes Python code safely in a controlled environment:

```python
executor = ExecutePythonCodePlugin(
    timeout_seconds=30,
    max_output_length=4000,
    restricted_modules=["subprocess", "ctypes"],
    allow_networking=False
)

result = executor.execute_python_code("""
import math
print(f"The square root of 16 is {math.sqrt(16)}")
""")
```

### 3. SKLogger

Provides detailed, colorful logging of the AI's thought process and execution:

```python
logger = SKLogger(
    name="PythonExecutor",
    level=LogLevel.DEBUG,
    colorize=True
)

logger.section("GENERATING CODE")
logger.llm_thinking("I need to create a function that calculates factorials...")
logger.llm_code("def factorial(n):\n    if n == 0:\n        return 1\n    return n * factorial(n-1)")
```

## 🔒 Security Considerations

The Python Executor Tool provides several security measures:

- **Module Restrictions**: Control which Python modules can be imported
- **Network Access Control**: Disable or enable network operations
- **File System Limitations**: Restrict file system operations
- **Execution Timeouts**: Prevent infinite loops or long-running code
- **Memory Limits**: Set maximum memory usage for code execution

Configure these settings when creating an ExecutePythonCodePlugin instance:

```python
executor = ExecutePythonCodePlugin(
    timeout_seconds=10,
    restricted_modules=["os", "subprocess", "sys", "importlib"],
    allow_networking=False,
    allow_file_write=False,
    memory_limit_mb=100
)
```

## 🔄 Integration with Semantic Kernel

The tool seamlessly integrates with Semantic Kernel's plugin architecture:

```python
kernel = Kernel()
kernel.add_service(BedrockChatCompletion(model_id=os.getenv("ANTHROPIC_MODEL_ID")))

# Add Python Code Generator plugin
python_generator = PythonCodeGeneratorPlugin()
kernel.add_plugin(python_generator, plugin_name="PythonCodeGenerator")

# Now you can use the plugin in AI conversations
result = await kernel.invoke_prompt(
    "{{$input}}\n\nUse the PythonCodeGenerator to solve this problem.",
    input_str="Calculate the sum of all prime numbers under 100."
)
```

## 📊 Advanced Examples

### Data Analysis and Visualization

```python
request = """
1. Load the Iris dataset from scikit-learn
2. Create a scatter plot of sepal length vs sepal width
3. Color the points by species
4. Add a title and axis labels
5. Save the plot as iris_scatter.png
"""

result = await python_generator.generate_and_execute_code(request)
```

### Web Scraping and Processing

```python
request = """
1. Download the list of Nobel Prize winners from Wikipedia
2. Extract the names and years for Physics category
3. Create a CSV file with the data
4. Print the first 5 entries
"""

result = await python_generator.generate_and_execute_code(request)
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgements

- [Microsoft Semantic Kernel](https://github.com/microsoft/semantic-kernel) team for the amazing framework
- [Anthropic](https://www.anthropic.com/) for Claude models

---

Built with ❤️ for AI developers who want to bridge the gap between natural language and Python execution.