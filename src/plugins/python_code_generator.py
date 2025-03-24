from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from semantic_kernel.contents import ChatMessageContent, TextContent
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.bedrock.bedrock_prompt_execution_settings import (
    BedrockChatPromptExecutionSettings,
)

import os
import re
from typing import List

from src.plugins.python_executor import ExecutePythonCodePlugin
from src.logger.sk_logger import SKLogger, LogLevel

class PythonCodeGeneratorPlugin:
    def __init__(self, model_id=None):
        self.model_id = model_id or os.getenv("ANTHROPIC_MODEL_ID")

        # Logger oluştur
        self.logger = SKLogger(
            name="PythonCodeGenerator",
            level=LogLevel.DEBUG,
            log_to_file=True,
            colorize=True,
            use_ascii_emoji=True
        )
        
        self.logger.section("INITIALIZING PYTHON CODE GENERATOR", LogLevel.INFO)

        self.system_prompt = """
        You are an expert Python code generator. Your task is to create functional,
        efficient, and secure Python code based on user requests.

        Steps to follow:

        1. PLAN: Analyze the user's request and create a solution plan
        2. DEPENDENCIES: Identify required libraries (standard library, third-party)
        3. CODE: Create working code and explain it
        4. TEST: Verify code works correctly, catch potential errors
        5. OPTIMIZE: Optimize code if necessary

        Important considerations when writing code:
        - Good error handling (try/except)
        - Safe file operations (using with blocks)
        - Proper exception handling
        - Memory efficiency
        - Security concerns

        When packages are missing:
        - Detect required packages
        - Install using pip install command
        - Verify installation success

        When errors occur:
        - Analyze error message
        - Identify error source
        - Generate and implement solution
        - Verify solution success

        Output format:
        1. Summary plan
        2. Required packages and installation code
        3. Main code block
        4. Test/validation code
        5. Explanations (when needed)

        Code must always be executable and fully accomplish the task specified by the user.
        
        IMPORTANT: Before writing code, explain your thought process with "THINKING:" prefix.
        Before writing code, describe your plan with "PLANNING:" prefix.
        
        Always include complete executable Python code in code blocks with ```python and ``` markers.
        """
        
        self.logger.debug(f"Creating BedrockChatCompletion with model: {self.model_id}")
        
        # Agent kullanmak yerine doğrudan BedrockChatCompletion kullan
        self.chat_service = BedrockChatCompletion(model_id=self.model_id)
        
        # Execution settings oluştur
        self.execution_settings = BedrockChatPromptExecutionSettings(
            max_tokens=4096,
            temperature=0.5,
        )
        
        # Executor oluştur
        self.executor = ExecutePythonCodePlugin(
            timeout_seconds=600,
            max_output_length=4000,
            restricted_modules=["subprocess", "ctypes", "socket"],
            allow_networking=True,
            allow_file_write=True,
        )
        
        self.logger.info("Python Code Generator initialized successfully")

    @kernel_function(
        description="Generate optimized and functional Python code based on user requirements",
        name="generate_python_code",
    )
    async def generate_python_code(self, request: str) -> str:
        """
        Kullanıcı isteğine göre Python kodu oluşturur.
        
        Args:
            request: Kullanıcının kod isteği
            
        Returns:
            Oluşturulan kod ve açıklamalar
        """
        self.logger.section(f"GENERATING CODE FOR: {request}", LogLevel.INFO)
        self.logger.info(f"Processing request: {request}")
        
        try:
            # Agent yerine doğrudan chat_service.complete_chat kullan
            self.logger.debug("Sending request to chat completion service...")
            
            # ChatHistory oluştur
            history = ChatHistory()
            history.add_system_message(self.system_prompt)
            history.add_user_message(request)
            
            # Mesajı gönder ve yanıtı al - settings parametresi eklendi
            result = await self.chat_service.get_chat_message_content(
                chat_history=history,
                settings=self.execution_settings,  # Önemli: settings parametresi
            )
            
            # Sonucu string'e dönüştür
            if isinstance(result, ChatMessageContent):
                response_content = result.content
            elif isinstance(result, TextContent):
                response_content = result.text
            elif isinstance(result, str):
                response_content = result
            else:
                response_content = str(result)
                
            self.logger.debug("Received response from chat completion service")
            
            # LLM çıktısını ayrıştır ve logla
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
        Kullanıcı isteğine göre Python kodu oluşturur ve hemen yürütür.
        
        Args:
            request: Kullanıcının kod isteği
            
        Returns:
            Kod oluşturma ve yürütme sonuçları
        """
        self.logger.section(f"GENERATING AND EXECUTING CODE FOR: {request}", LogLevel.INFO)
        
        # Asenkron fonksiyonu çağır
        generated_code = await self.generate_python_code(request)
        
        # Hata kontrolü
        if generated_code.startswith("Error generating code:"):
            return f"Failed to generate code: {generated_code}"
        
        # Kodu çıkar
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
        
        combined_result = f"# Generated Code\n\n{generated_code}\n\n# Execution Results\n\n"
        for i, result in enumerate(execution_results):
            combined_result += f"## Block {i+1} Result\n{result}\n\n"
            
        return combined_result
    
    def _extract_code_blocks(self, text: str) -> List[str]:
        """Markdown formatındaki metinden kod bloklarını çıkarır"""
        import re
        
        # Python kod bloklarını ara
        pattern = r'```(?:python)?\s*([\s\S]*?)```'
        code_blocks = re.findall(pattern, text)
        
        if not code_blocks:
            # Kod bloğu bulunamazsa, tüm metni kod olarak kabul et
            if "print(" in text or "import " in text:
                return [text]
            return []
            
        return code_blocks
    
    def _parse_and_log_llm_output(self, text: str, request: str):
        """LLM çıktısını ayrıştır ve uygun şekilde logla"""
        
        # Düşünme ve planlama bölümlerini bul
        thinking_match = re.search(r'THINKING:(.*?)(?=PLANNING:|```|$)', text, re.DOTALL)
        planning_match = re.search(r'PLANNING:(.*?)(?=```|$)', text, re.DOTALL)
        
        thinking = thinking_match.group(1).strip() if thinking_match else ""
        planning = planning_match.group(1).strip() if planning_match else ""
        
        if thinking:
            self.logger.llm_thinking(thinking)
        
        if planning:
            self.logger.llm_planning(planning)
        
        # Kod bloklarını bul
        code_blocks = self._extract_code_blocks(text)
        for i, code in enumerate(code_blocks):
            if code.strip():
                self.logger.llm_code(code)

