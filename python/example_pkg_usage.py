"""
Semantic Kernel Tools Package Usage Example
"""


def main():
    try:
        import semantic_kernel_plugins

        print("Semantic Kernel Plugins successfully imported!")
        print(f"Version: {semantic_kernel_plugins.__version__}")

        # Create logger
        logger = semantic_kernel_plugins.SKLogger(
            name="TestLogger", use_ascii_emoji=True
        )
        logger.info("Logger successfully initialized")

        # Create Python executor
        executor = semantic_kernel_plugins.ExecutePythonCodePlugin(
            timeout_seconds=10, allow_networking=True
        )

        # Run test code
        test_code = """
        import math
        print("Python code execution test with Semantic Kernel Tools")
        print(f"Value of Pi: {math.pi}")
        """

        result = executor.execute_python_code(test_code)
        print("\nExecution result:")
        print(result)

    except ImportError:
        print("Semantic Kernel Plugins package not found!")
        print("To install: pip install semantic_kernel_plugins")

    except Exception as e:
        print(f"Error occurred: {e}")


if __name__ == "__main__":
    main()
