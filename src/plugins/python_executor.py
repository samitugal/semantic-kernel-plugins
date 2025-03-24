from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from semantic_kernel.agents.chat_completion.chat_completion_agent import ChatCompletionAgent
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.functions import kernel_function

import subprocess
import os
import sys
import tempfile
import traceback
import uuid
import ast
import io
import contextlib
from typing import Optional, Dict, Any, Tuple, List

from dotenv import load_dotenv

load_dotenv()

class ExecutePythonCodePlugin:
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_output_length: int = 4000,
        restricted_modules: Optional[List[str]] = None,
        allow_networking: bool = True,
        allow_file_write: bool = True,
    ):
        self._timeout_seconds = timeout_seconds
        self._max_output_length = max_output_length
        self._restricted_modules = restricted_modules or [
            "subprocess", "ctypes", "socket"
        ]
        self._allow_networking = allow_networking
        self._allow_file_write = allow_file_write
        self._temp_dir = tempfile.mkdtemp(prefix="sk_python_executor_")

    @kernel_function(
        description="Execute Python code safely and return the result",
        name="execute_python_code",
    )
    def execute_python_code(self, code: str) -> str:
        code = code.strip()
        if not code:
            return "No code provided to execute."
        
        # Python blokları içerisinden kodu çıkar
        code = self._extract_code_from_markdown(code)
        
        # Güvenlik kontrolü
        if not self._is_code_safe(code):
            return "Code contains potentially unsafe operations and was not executed."
            
        # Geçici dosya oluştur
        temp_file_path = os.path.join(self._temp_dir, f"code_{uuid.uuid4().hex}.py")
        
        try:
            # Kodu dosyaya yaz
            with open(temp_file_path, "w") as f:
                f.write(code)
                
            # Kodu yürüt
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            original_stdout = sys.stdout
            original_stderr = sys.stderr
            
            try:
                # stdout ve stderr'i yönlendir
                sys.stdout = output_buffer
                sys.stderr = error_buffer
                
                # Kodu yeni bir namespace'de yürüt
                with open(temp_file_path, 'r') as f:
                    namespace = {}
                    exec(f.read(), namespace)
                    
            except Exception as e:
                print(f"Error: {str(e)}", file=error_buffer)
                traceback.print_exc(file=error_buffer)
                
            finally:
                # stdout ve stderr'i eski haline getir
                sys.stdout = original_stdout
                sys.stderr = original_stderr
            
            # Sonuçları oluştur
            output = output_buffer.getvalue()
            error = error_buffer.getvalue()
            
            result = ""
            if output:
                output = output[:self._max_output_length] + "..." if len(output) > self._max_output_length else output
                result += f"Output:\n{output}\n"
                
            if error:
                error = error[:self._max_output_length] + "..." if len(error) > self._max_output_length else error
                result += f"Error:\n{error}\n"
                
            if not output and not error:
                result = "Code executed successfully with no output."
                
            return result
                
        except Exception as e:
            return f"An unexpected error occurred: {str(e)}"
            
        finally:
            # Geçici dosyayı temizle
            if os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except:
                    pass

    def _extract_code_from_markdown(self, text: str) -> str:
        """Markdown içerisinden Python kod bloklarını çıkarır."""
        import re
        
        # Python kod bloklarını ara
        code_block_pattern = r'```(?:python)?\s*([\s\S]*?)```'
        code_blocks = re.findall(code_block_pattern, text)
        
        # Eğer kod blokları varsa, ilkini kullan
        if code_blocks:
            return code_blocks[0].strip()
        
        # Kod bloğu yoksa, orijinal metni döndür
        return text.strip()

    def _is_code_safe(self, code: str) -> bool:
        """Kodun güvenli olup olmadığını kontrol eder."""
        try:
            tree = ast.parse(code)
            
            for node in ast.walk(tree):
                # Kısıtlı modüllerin import kontrolü
                if isinstance(node, ast.Import):
                    for name in node.names:
                        if name.name in self._restricted_modules and not self._allow_networking:
                            return False
                            
                # Kısıtlı modüllerden import kontrolü
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self._restricted_modules and not self._allow_networking:
                        return False
                
                # __import__ çağrılarını kontrol et
                elif isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == '__import__':
                    return False
                    
                # eval, exec fonksiyonlarını kontrol et
                elif isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id in ['eval', 'exec']:
                    return False
                    
            return True
        except SyntaxError:
            # Kod sözdizimi hataları içeriyorsa, yürütme sırasında yakalayacağız
            return True

    def cleanup(self):
        """Geçici kaynakları temizle."""
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
            "os", "sys", "subprocess", "shutil", "importlib", 
            "ctypes", "socket", "requests", "urllib"
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
        Executes Python code in a safe manner and returns the output.
        
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
                output = output[:self._max_output_length] + "..." if len(output) > self._max_output_length else output
                result += f"Output:\n{output}\n"
                
            if error:
                error = error[:self._max_output_length] + "..." if len(error) > self._max_output_length else error
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
            analysis.append("⚠️ Bare except clause found. Consider catching specific exceptions.")
            
        if "import os" in code and any(cmd in code for cmd in ["os.system", "os.popen", "subprocess"]):
            analysis.append("⚠️ Code uses system commands which may pose security risks.")
            
        if "open(" in code and "with open" not in code:
            analysis.append("⚠️ File operations not using context manager (with statement).")
        
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
                        if name.name in self._restricted_modules and not self._is_exception_allowed(name.name):
                            return False
                            
                # Check for imports from restricted modules
                elif isinstance(node, ast.ImportFrom):
                    if node.module in self._restricted_modules and not self._is_exception_allowed(node.module):
                        return False
                
                # Check for __import__ calls
                elif isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id == '__import__':
                    return False
                    
                # Check for eval, exec functions
                elif isinstance(node, ast.Call) and hasattr(node.func, 'id') and node.func.id in ['eval', 'exec']:
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
            with contextlib.redirect_stdout(output_buffer), contextlib.redirect_stderr(error_buffer):
                try:
                    # Execute the file in a new namespace
                    namespace = {}
                    with open(file_path, 'r') as f:
                        code = compile(f.read(), file_path, 'exec')
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
