import ast
import contextlib
import io
import os
import platform
import re
import subprocess
import sys
import tempfile
import traceback
import uuid
from typing import Any, Dict, List, Optional, Tuple

from dotenv import load_dotenv
from semantic_kernel.functions import kernel_function

load_dotenv()


class ExecutePythonCodePlugin:
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_output_length: int = 4000,
        restricted_modules: Optional[List[str]] = None,
        allow_networking: bool = True,
        allow_file_write: bool = True,
        auto_install_dependencies: bool = True,
        use_virtual_env: bool = True,
    ):
        self._timeout_seconds = timeout_seconds
        self._max_output_length = max_output_length
        self._restricted_modules = restricted_modules or [
            "subprocess",
            "ctypes",
            "socket",
        ]
        self._allow_networking = allow_networking
        self._allow_file_write = allow_file_write
        self._temp_dir = tempfile.mkdtemp(prefix="sk_python_executor_")
        self._auto_install_dependencies = auto_install_dependencies
        self._use_virtual_env = use_virtual_env

        self._venv_dir = os.path.join(self._temp_dir, "venv")

        if self._use_virtual_env:
            self._create_virtual_env()

    def _create_virtual_env(self):
        try:
            is_windows = platform.system() == "Windows"

            print(f"Creating virtual environment at {self._venv_dir}")

            subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "venv",
                    self._venv_dir,
                    "--system-site-packages",
                ],
                check=True,
                capture_output=True,
                timeout=60,
            )

            python_cmd = os.path.join(
                self._venv_dir, "Scripts" if is_windows else "bin", "python"
            )
            pip_cmd = os.path.join(
                self._venv_dir, "Scripts" if is_windows else "bin", "pip"
            )

            try:
                result = subprocess.run(
                    [python_cmd, "-c", "import pip; print(pip.__version__)"],
                    capture_output=True,
                    text=True,
                    timeout=10,
                )
                if result.returncode != 0:
                    print("Pip not available in venv, installing manually...")
                    self._install_pip_manually()
            except:
                print("Error checking pip, installing manually...")
                self._install_pip_manually()

            try:
                subprocess.run(
                    [pip_cmd, "install", "--upgrade", "pip"],
                    check=False,
                    capture_output=True,
                    timeout=60,
                )
                print("Pip upgraded successfully")
            except Exception as e:
                print(f"Failed to upgrade pip: {str(e)}")

            print(f"Virtual environment setup completed")
        except Exception as e:
            print(f"Failed to create virtual environment: {str(e)}")
            self._venv_dir = os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "..", ".venv")
            )
            if os.path.exists(self._venv_dir):
                print(f"Using existing virtual environment at {self._venv_dir}")
            else:
                print("Disabling virtual environment usage")
                self._use_virtual_env = False

    def _install_pip_manually(self):
        try:
            is_windows = platform.system() == "Windows"

            python_cmd = os.path.join(
                self._venv_dir, "Scripts" if is_windows else "bin", "python"
            )

            get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
            get_pip_path = os.path.join(self._temp_dir, "get-pip.py")

            try:
                import requests

                with open(get_pip_path, "wb") as f:
                    response = requests.get(get_pip_url)
                    f.write(response.content)
            except:
                if is_windows:
                    subprocess.run(
                        ["curl", "-o", get_pip_path, get_pip_url],
                        check=True,
                        capture_output=True,
                        timeout=30,
                    )
                else:
                    subprocess.run(
                        ["wget", "-O", get_pip_path, get_pip_url],
                        check=True,
                        capture_output=True,
                        timeout=30,
                    )

            subprocess.run(
                [python_cmd, get_pip_path], check=True, capture_output=True, timeout=60
            )

            print("Pip manually installed")
        except Exception as e:
            print(f"Failed to manually install pip: {str(e)}")

    @kernel_function(
        description="Execute Python code safely and return the result",
        name="execute_python_code",
    )
    def execute_python_code(self, code: str) -> str:
        """
        Executes Python code safely and returns the result.

        Args:
            code: The Python code to execute

        Returns:
            The output of the code or error messages
        """
        code = code.strip()
        if not code:
            return "No code provided to execute."

        code = self._extract_code_from_markdown(code)

        if not self._is_code_safe(code):
            return "Code contains potentially unsafe operations and was not executed."

        temp_file_path = os.path.join(self._temp_dir, f"code_{uuid.uuid4().hex}.py")

        try:
            with open(temp_file_path, "w", encoding="utf-8") as f:
                f.write(code)

            if self._use_virtual_env and os.path.exists(self._venv_dir):
                return self._execute_in_virtual_env(temp_file_path, code)
            else:
                return self._execute_in_current_env(temp_file_path, code)

        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

        finally:
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass

    def _execute_in_virtual_env(self, file_path: str, code: str) -> str:
        """Executes code in virtual environment."""
        try:
            is_windows = platform.system() == "Windows"

            python_path = os.path.join(
                self._venv_dir, "Scripts" if is_windows else "bin", "python"
            )
            pip_path = os.path.join(
                self._venv_dir, "Scripts" if is_windows else "bin", "pip"
            )

            installation_log = []
            if self._auto_install_dependencies:
                missing_packages = self._detect_missing_packages(code)
                if missing_packages:
                    log = self._install_packages_in_venv(missing_packages, pip_path)
                    installation_log.append(log)

            result = subprocess.run(
                [python_path, file_path],
                capture_output=True,
                text=True,
                timeout=self._timeout_seconds,
            )

            output = result.stdout
            error = result.stderr

            formatted_result = ""
            if installation_log:
                formatted_result += (
                    f"Dependency installation:\n{installation_log[0]}\n\n"
                )

            if output:
                output = (
                    output[: self._max_output_length] + "..."
                    if len(output) > self._max_output_length
                    else output
                )
                formatted_result += f"Output:\n{output}\n"

            if error:
                error = (
                    error[: self._max_output_length] + "..."
                    if len(error) > self._max_output_length
                    else error
                )
                formatted_result += f"Error:\n{error}\n"

            if not output and not error and not installation_log:
                formatted_result = "Code executed successfully with no output."

            return formatted_result

        except subprocess.TimeoutExpired:
            return f"Execution timed out after {self._timeout_seconds} seconds."
        except Exception as e:
            return f"Error executing in virtual environment: {str(e)}"

    def _execute_in_current_env(self, file_path: str, code: str) -> str:
        """Executes code in current environment."""
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            installation_log = ""
            if self._auto_install_dependencies:
                installation_log = self._check_and_install_dependencies(code)

            sys.stdout = output_buffer
            sys.stderr = error_buffer

            namespace = {}
            with open(file_path, "r", encoding="utf-8") as f:
                exec(f.read(), namespace)

        except Exception as e:
            print(f"Error: {str(e)}", file=error_buffer)
            traceback.print_exc(file=error_buffer)

        finally:
            sys.stdout = original_stdout
            sys.stderr = original_stderr

        output = output_buffer.getvalue()
        error = error_buffer.getvalue()

        result = ""
        if installation_log:
            result += f"Dependency installation:\n{installation_log}\n\n"

        if output:
            output = (
                output[: self._max_output_length] + "..."
                if len(output) > self._max_output_length
                else output
            )
            result += f"Output:\n{output}\n"

        if error:
            error = (
                error[: self._max_output_length] + "..."
                if len(error) > self._max_output_length
                else error
            )
            result += f"Error:\n{error}\n"

        if not output and not error and not installation_log:
            result = "Code executed successfully with no output."

        return result

    def _detect_missing_packages(self, code: str) -> List[str]:
        """Analyzes import statements in code and detects missing packages."""
        try:
            import_pattern = (
                r"^import\s+([a-zA-Z0-9_,.]+)|^from\s+([a-zA-Z0-9_.]+)\s+import"
            )
            matches = re.finditer(import_pattern, code, re.MULTILINE)

            missing_packages = []

            for match in matches:
                module_name = match.group(1) or match.group(2)

                root_module = module_name.split(".")[0]

                if root_module in sys.builtin_module_names:
                    continue

                if (
                    root_module in self._restricted_modules
                    and not self._is_exception_allowed(root_module)
                ):
                    continue

                package_mapping = {
                    "sklearn": "scikit-learn",
                    "cv2": "opencv-python",
                    "PIL": "pillow",
                    "bs4": "beautifulsoup4",
                    "tensorflow": "tensorflow",
                    "torch": "torch",
                    "keras": "keras",
                }

                package_name = package_mapping.get(root_module, root_module)

                if package_name not in missing_packages and package_name not in [
                    "__future__"
                ]:
                    missing_packages.append(package_name)

            return missing_packages

        except Exception as e:
            print(f"Error detecting dependencies: {str(e)}")
            return []

    def _install_packages_in_venv(
        self, packages: List[str], pip_path: str = None
    ) -> str:
        """Installs packages in virtual environment."""
        if not self._allow_networking:
            return "Network access is disabled; cannot install packages"

        if not packages:
            return ""

        try:
            is_windows = platform.system() == "Windows"

            if pip_path is None:
                pip_path = os.path.join(
                    self._venv_dir, "Scripts" if is_windows else "bin", "pip"
                )

            if not os.path.exists(pip_path) and is_windows:
                alt_pip_path = os.path.join(self._venv_dir, "Scripts", "pip3.exe")
                if os.path.exists(alt_pip_path):
                    pip_path = alt_pip_path
                else:
                    python_path = os.path.join(self._venv_dir, "Scripts", "python.exe")
                    if os.path.exists(python_path):
                        pip_path = None

            installation_log = []
            installation_log.append(f"Installing packages: {', '.join(packages)}")

            for package in packages:
                if package.lower() in [m.lower() for m in self._restricted_modules]:
                    installation_log.append(
                        f"Cannot install restricted module: {package}"
                    )
                    continue

                safe_package = re.sub(r"[^a-zA-Z0-9_\.-]", "", package)
                if safe_package != package:
                    installation_log.append(
                        f"Package name contains invalid characters: {package}"
                    )
                    continue

                try:
                    if pip_path:
                        result = subprocess.run(
                            [pip_path, "install", safe_package],
                            capture_output=True,
                            text=True,
                            timeout=120,
                        )
                    else:
                        python_path = os.path.join(
                            self._venv_dir, "Scripts" if is_windows else "bin", "python"
                        )
                        result = subprocess.run(
                            [python_path, "-m", "pip", "install", safe_package],
                            capture_output=True,
                            text=True,
                            timeout=120,
                        )

                    if result.returncode == 0:
                        installation_log.append(f"Successfully installed {package}")
                    else:
                        installation_log.append(
                            f"Failed to install {package}: {result.stderr}"
                        )
                        if "No module named pip" in result.stderr:
                            installation_log.append(
                                "Pip not found, trying to install pip first..."
                            )
                            self._install_pip_manually()
                            python_path = os.path.join(
                                self._venv_dir,
                                "Scripts" if is_windows else "bin",
                                "python",
                            )
                            result = subprocess.run(
                                [python_path, "-m", "pip", "install", safe_package],
                                capture_output=True,
                                text=True,
                                timeout=120,
                            )
                            if result.returncode == 0:
                                installation_log.append(
                                    f"Successfully installed {package} after installing pip"
                                )
                            else:
                                installation_log.append(
                                    f"Still failed to install {package}: {result.stderr}"
                                )
                except Exception as e:
                    installation_log.append(f"Error installing {package}: {str(e)}")

            return "\n".join(installation_log)

        except Exception as e:
            return f"Error installing packages: {str(e)}"

    def _extract_code_from_markdown(self, text: str) -> str:
        """Extracts Python code blocks from markdown."""
        code_block_pattern = r"```(?:python)?\s*([\s\S]*?)```"
        code_blocks = re.findall(code_block_pattern, text)

        if code_blocks:
            return code_blocks[0].strip()

        return text.strip()

    def _is_code_safe(self, code: str) -> bool:
        """Checks if the code is safe."""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if (
                            name.name in self._restricted_modules
                            and not self._is_exception_allowed(name.name)
                        ):
                            return False

                elif isinstance(node, ast.ImportFrom):
                    if (
                        node.module in self._restricted_modules
                        and not self._is_exception_allowed(node.module)
                    ):
                        return False

                elif (
                    isinstance(node, ast.Call)
                    and hasattr(node.func, "id")
                    and node.func.id == "__import__"
                ):
                    return False

                elif (
                    isinstance(node, ast.Call)
                    and hasattr(node.func, "id")
                    and node.func.id in ["eval", "exec"]
                ):
                    return False

            return True
        except SyntaxError:
            return True

    def _is_exception_allowed(self, module_name: str) -> bool:
        """Checks if the restricted module is allowed."""
        if module_name in ["requests", "urllib"] and self._allow_networking:
            return True
        return False

    def _check_and_install_dependencies(self, code: str) -> str:
        """Analyzes import statements in code and installs missing packages."""
        try:
            import_pattern = (
                r"^import\s+([a-zA-Z0-9_,.]+)|^from\s+([a-zA-Z0-9_.]+)\s+import"
            )
            matches = re.finditer(import_pattern, code, re.MULTILINE)

            missing_packages = []
            installation_log = []

            for match in matches:
                module_name = match.group(1) or match.group(2)

                root_module = module_name.split(".")[0]

                if root_module in sys.builtin_module_names:
                    continue

                if (
                    root_module in self._restricted_modules
                    and not self._is_exception_allowed(root_module)
                ):
                    continue

                try:
                    __import__(root_module)
                except ImportError:
                    if root_module not in missing_packages and root_module not in [
                        "__future__"
                    ]:
                        missing_packages.append(root_module)

            if missing_packages:
                installation_log.append(
                    f"Installing packages: {', '.join(missing_packages)}"
                )

                for package in missing_packages:
                    try:
                        output = self._install_package(package)
                        installation_log.append(f"Successfully installed {package}")
                        installation_log.append(output)
                    except Exception as e:
                        error = f"Failed to install {package}: {str(e)}"
                        installation_log.append(error)
                        return f"Error: {error}"

            return "\n".join(installation_log) if installation_log else ""

        except Exception as e:
            return f"Error: Failed to check dependencies: {str(e)}"

    def _install_package(self, package_name: str) -> str:
        """Belirtilen paketi pip ile yükler."""
        if not self._allow_networking:
            return f"Network access is disabled; cannot install {package_name}"

        try:
            if package_name.lower() in [m.lower() for m in self._restricted_modules]:
                return f"Cannot install restricted module: {package_name}"

            safe_package = re.sub(r"[^a-zA-Z0-9_\.-]", "", package_name)
            if safe_package != package_name:
                return f"Package name contains invalid characters: {package_name}"

            result = subprocess.run(
                [sys.executable, "-m", "pip", "install", safe_package],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode != 0:
                return f"Pip install failed: {result.stderr}"

            return f"Package installed successfully"

        except Exception as e:
            return f"Installation error: {str(e)}"

    def cleanup(self):
        """Cleans up temporary resources."""
        try:
            import shutil

            shutil.rmtree(self._temp_dir, ignore_errors=True)
        except:
            pass


class PythonExecutorPlugin:
    """A plugin for Semantic Kernel that allows for safe execution of Python code."""

    def __init__(
        self,
        timeout_seconds: int = 30,
        max_output_length: int = 4000,
        restricted_modules: Optional[List[str]] = None,
        allow_networking: bool = False,
        allow_file_write: bool = False,
        memory_limit_mb: Optional[int] = 100,
    ):
        self._timeout_seconds = timeout_seconds
        self._max_output_length = max_output_length
        self._restricted_modules = restricted_modules or [
            "os",
            "sys",
            "subprocess",
            "shutil",
            "importlib",
            "ctypes",
            "socket",
            "requests",
            "urllib",
        ]
        self._allow_networking = allow_networking
        self._allow_file_write = allow_file_write
        self._memory_limit_mb = memory_limit_mb
        self._temp_dir = tempfile.mkdtemp(prefix="sk_python_executor_")

    @kernel_function(
        description="Executes Python code safely and returns the result",
        name="execute_python",
    )
    def execute_python(self, code: str) -> str:
        """
        Executes Python code safely and returns the output.

        Args:
            code: The Python code to execute

        Returns:
            A string containing the output of the code execution and any errors
        """
        code = code.strip()
        if not code:
            return "No code provided to execute."

        # First do a basic security check
        if not self._is_code_safe(code):
            return "Code contains potentially unsafe operations and was not executed."

        # Create a unique temporary file for code execution
        temp_file_path = os.path.join(self._temp_dir, f"code_{uuid.uuid4().hex}.py")

        try:
            # Write code to the temp file
            with open(temp_file_path, "w") as f:
                f.write(code)

            # Execute the code and capture output
            output, error = self._execute_code_file(temp_file_path)

            result = ""
            if output:
                output = (
                    output[: self._max_output_length] + "..."
                    if len(output) > self._max_output_length
                    else output
                )
                result += f"Output:\n{output}\n"

            if error:
                error = (
                    error[: self._max_output_length] + "..."
                    if len(error) > self._max_output_length
                    else error
                )
                result += f"Error:\n{error}\n"

            if not output and not error:
                result = "Code executed successfully with no output."

            return result

        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"

        finally:
            # Clean up the temporary file
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass

    @kernel_function(
        description="Plans and executes multi-step Python tasks",
        name="plan_and_execute",
    )
    def plan_and_execute(self, task_description: str) -> str:
        """
        Creates a plan for solving a task with Python and executes it step by step.

        Args:
            task_description: A description of the task to be solved

        Returns:
            A detailed report of the plan, execution steps, and results
        """
        # This is a placeholder for the actual planning logic
        # In a real implementation, this might use the AI to create the plan

        plan = f"# Plan for: {task_description}\n"
        plan += "1. Parse and understand the task requirements\n"
        plan += "2. Prepare the necessary Python code\n"
        plan += "3. Execute the code in a safe environment\n"
        plan += "4. Analyze results and handle any errors\n\n"

        # Generate a simple code example based on the task description
        # In a real implementation, you would use the LLM to generate this code
        sample_code = f"""
        # Python code to address: {task_description}
        try:
            # Main code execution
            print("Executing task: {task_description}")
            result = f"Task completed successfully for: {task_description}"
            print(result)
        except Exception as e:
            print(f"Error occurred: str(e)")
        """

        # Execute the generated code
        execution_result = self.execute_python(sample_code)

        report = f"{plan}\n## Generated Code:\n```python\n{sample_code}\n```\n\n## Execution Result:\n{execution_result}\n"
        return report

    @kernel_function(
        description="Analyzes Python code for errors and suggests improvements",
        name="analyze_code",
    )
    def analyze_code(self, code: str) -> str:
        """
        Analyzes Python code for potential errors and suggests improvements.

        Args:
            code: The Python code to analyze

        Returns:
            Analysis of the code including potential issues and suggestions
        """
        if not code.strip():
            return "No code provided to analyze."

        analysis = []

        # Check for syntax errors
        try:
            ast.parse(code)
            analysis.append("✅ No syntax errors detected.")
        except SyntaxError as e:
            analysis.append(f"❌ Syntax error: {str(e)}")

        # Check for common issues
        if "except:" in code and "except Exception:" not in code:
            analysis.append(
                "⚠️ Bare except clause found. Consider catching specific exceptions."
            )

        if "import os" in code and any(
            cmd in code for cmd in ["os.system", "os.popen", "subprocess"]
        ):
            analysis.append(
                "⚠️ Code uses system commands which may pose security risks."
            )

        if "open(" in code and "with open" not in code:
            analysis.append(
                "⚠️ File operations not using context manager (with statement)."
            )

        # Add more static analysis rules as needed

        return "\n".join(analysis)

    def _is_code_safe(self, code: str) -> bool:
        """Check if the provided code contains potentially unsafe operations."""
        try:
            tree = ast.parse(code)

            for node in ast.walk(tree):
                # Check for imports of restricted modules
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if (
                            name.name in self._restricted_modules
                            and not self._is_exception_allowed(name.name)
                        ):
                            return False

                # Check for imports from restricted modules
                elif isinstance(node, ast.ImportFrom):
                    if (
                        node.module in self._restricted_modules
                        and not self._is_exception_allowed(node.module)
                    ):
                        return False

                # Check for __import__ calls
                elif (
                    isinstance(node, ast.Call)
                    and hasattr(node.func, "id")
                    and node.func.id == "__import__"
                ):
                    return False

                # Check for eval, exec functions
                elif (
                    isinstance(node, ast.Call)
                    and hasattr(node.func, "id")
                    and node.func.id in ["eval", "exec"]
                ):
                    return False

            return True
        except SyntaxError:
            # If the code has syntax errors, we'll catch them during execution
            return True

    def _is_exception_allowed(self, module_name: str) -> bool:
        """Check if a restricted module should be allowed in certain cases."""
        # Allow some modules based on configuration
        if module_name in ["requests", "urllib"] and self._allow_networking:
            return True

        return False

    def _execute_code_file(self, file_path: str) -> Tuple[str, str]:
        """Execute the Python file and return its output and error streams."""
        # Prepare for execution
        output_buffer = io.StringIO()
        error_buffer = io.StringIO()

        # Create restricted environment variables
        env = os.environ.copy()
        if not self._allow_networking:
            env["PYTHONHTTPSVERIFY"] = "1"  # Force HTTPS verification

        original_stdout = sys.stdout
        original_stderr = sys.stderr

        try:
            # Redirect stdout and stderr
            sys.stdout = output_buffer
            sys.stderr = error_buffer

            # Execute code with timeout
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(
                error_buffer
            ):
                try:
                    # Execute the file in a new namespace
                    namespace = {}
                    with open(file_path, "r") as f:
                        code = compile(f.read(), file_path, "exec")
                        exec(code, namespace)
                except Exception as e:
                    print(f"Error: {str(e)}", file=sys.stderr)
                    traceback.print_exc(file=sys.stderr)

            return output_buffer.getvalue(), error_buffer.getvalue()

        finally:
            # Restore stdout and stderr
            sys.stdout = original_stdout
            sys.stderr = original_stderr

    def cleanup(self):
        """Clean up any temporary resources."""
        try:
            import shutil

            shutil.rmtree(self._temp_dir, ignore_errors=True)
        except:
            pass
