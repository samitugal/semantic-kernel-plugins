import os
import re
from typing import List, Optional

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.chat_completion_client_base import \
    ChatCompletionClientBase
from semantic_kernel.connectors.ai.prompt_execution_settings import \
    PromptExecutionSettings
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions import kernel_function

from semantic_kernel_tools.logger.sk_logger import LogLevel, SKLogger
from semantic_kernel_tools.tools.python_executor import ExecutePythonCodePlugin


class PythonCodeGeneratorPlugin:
    def __init__(
        self,
        chat_service: ChatCompletionClientBase,
        execution_settings: PromptExecutionSettings,
    ):
        self.chat_service = chat_service

        self.kernel = Kernel()
        self.kernel.add_service(chat_service)

        self.logger = SKLogger(
            name="PythonCodeGenerator",
            level=LogLevel.DEBUG,
            log_to_file=True,
            colorize=True,
            use_ascii_emoji=True,
        )

        self.logger.section("INITIALIZING PYTHON CODE GENERATOR", LogLevel.INFO)

        self.system_prompt = """
        You are an expert Python code generator. Your task is to create functional,
        efficient, and secure Python code based on user requests.

        Steps to follow:

        1. PLAN: Analyze the user's request and create a solution plan
        2. DEPENDENCIES: Identify required libraries (standard library, third-party)
           - Freely use any Python package that would be helpful for the task
           - The system will automatically install any missing packages
           - Don't hesitate to use specialized libraries when appropriate
        3. CODE: Create working code and explain it
        4. TEST: Verify code works correctly, catch potential errors
        5. OPTIMIZE: Optimize code if necessary

        Important considerations when writing code:
        - Good error handling (try/except)
        - Safe file operations (using with blocks)
        - Proper exception handling
        - Memory efficiency
        - Security concerns

        When using external libraries:
        - Import all necessary libraries at the top of your code
        - Feel free to use visualization libraries like matplotlib, seaborn, or plotly
        - Use data processing libraries like pandas, numpy, or scipy as needed
        - Utilize any specialized library that would make the solution more elegant

        Output format:
        1. Summary plan
        2. Required packages list
        3. Main code block
        4. Test/validation code
        5. Explanations (when needed)

        Code must always be executable and fully accomplish the task specified by the user.
        
        IMPORTANT: Before writing code, explain your thought process with "THINKING:" prefix.
        Before writing code, describe your plan with "PLANNING:" prefix.
        
        Always include complete executable Python code in code blocks with ```python and ``` markers.
        """

        self.logger.debug(
            f"Creating Chat Completion Service {self.chat_service.ai_model_id}"
        )

        self.execution_settings = execution_settings

        self.executor = ExecutePythonCodePlugin(
            timeout_seconds=600,
            max_output_length=4000,
            restricted_modules=["subprocess", "ctypes", "socket"],
            allow_networking=True,
            allow_file_write=True,
            auto_install_dependencies=True,
            use_virtual_env=True,
        )

        self.logger.info("Python Code Generator initialized successfully")

    @kernel_function(
        description="Generate optimized and functional Python code based on user requirements",
        name="generate_python_code",
    )
    async def generate_python_code(self, request: str) -> str:
        """
        Generates Python code based on user request.

        Args:
            request: User's code request

        Returns:
            Generated code and explanations
        """
        self.logger.section(f"GENERATING CODE FOR: {request}", LogLevel.INFO)
        self.logger.info(f"Processing request: {request}")

        try:
            self.logger.debug("Sending request to chat completion service...")

            history = ChatHistory()
            history.add_system_message(self.system_prompt)
            history.add_user_message(request)

            result = await self.chat_service.get_chat_message_content(
                chat_history=history,
                settings=self.execution_settings,
                kernel=self.kernel,
            )

            if isinstance(result, ChatMessageContent):
                response_content = result.content
            elif isinstance(result, TextContent):
                response_content = result.text
            elif isinstance(result, str):
                response_content = result
            else:
                response_content = str(result)

            self.logger.debug("Received response from chat completion service")

            self._parse_and_log_llm_output(response_content, request)

            return response_content

        except Exception as e:
            error_msg = f"Error generating code: {str(e)}"
            self.logger.error(error_msg)
            self.logger.error(f"Exception type: {type(e)}")
            import traceback

            self.logger.error(f"Traceback: {traceback.format_exc()}")
            return error_msg

    @kernel_function(
        description="Generate and execute Python code in one step",
        name="generate_and_execute_code",
    )
    async def generate_and_execute_code(self, request: str) -> str:
        """
        Generates and immediately executes Python code based on user request.

        Args:
            request: User's code request

        Returns:
            Code generation and execution results
        """
        self.logger.section(
            f"GENERATING AND EXECUTING CODE FOR: {request}", LogLevel.INFO
        )

        generated_code = await self.generate_python_code(request)

        if generated_code.startswith("Error generating code:"):
            return f"Failed to generate code: {generated_code}"

        code_blocks = self._extract_code_blocks(generated_code)

        execution_results = []
        for i, code in enumerate(code_blocks):
            if not code.strip():
                continue

            self.logger.info(f"Executing code block {i+1}/{len(code_blocks)}")
            self.logger.llm_code(code)

            execution_result = self.executor.execute_python_code(code)

            success = "Error:" not in execution_result
            self.logger.llm_execution(execution_result, success)

            execution_results.append(execution_result)

        combined_result = (
            f"# Generated Code\n\n{generated_code}\n\n# Execution Results\n\n"
        )
        for i, result in enumerate(execution_results):
            combined_result += f"## Block {i+1} Result\n{result}\n\n"

        return combined_result

    def _extract_code_blocks(self, text: str) -> List[str]:
        pattern = r"```(?:python)?\s*([\s\S]*?)```"
        code_blocks = re.findall(pattern, text)

        if not code_blocks:
            if "print(" in text or "import " in text:
                return [text]
            return []

        return code_blocks

    def _parse_and_log_llm_output(self, text: str, request: str):
        thinking_match = re.search(
            r"THINKING:(.*?)(?=PLANNING:|```|$)", text, re.DOTALL
        )
        planning_match = re.search(r"PLANNING:(.*?)(?=```|$)", text, re.DOTALL)

        thinking = thinking_match.group(1).strip() if thinking_match else ""
        planning = planning_match.group(1).strip() if planning_match else ""

        if thinking:
            self.logger.llm_thinking(thinking)

        if planning:
            self.logger.llm_planning(planning)

        code_blocks = self._extract_code_blocks(text)
        for i, code in enumerate(code_blocks):
            if code.strip():
                self.logger.llm_code(code)
