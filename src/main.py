import asyncio
import os
import logging
import atexit

from semantic_kernel import Kernel
from semantic_kernel.utils.logging import setup_logging
from semantic_kernel.functions import kernel_function
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments

from semantic_kernel.connectors.ai.bedrock.bedrock_prompt_execution_settings import (
    BedrockChatPromptExecutionSettings,
)

from dotenv import load_dotenv

from src.plugins.tavily_web_search import TavilySearchPlugin
from src.plugins.python_code_generator import PythonCodeGeneratorPlugin
from src.logger.sk_logger import SKLogger, LogLevel

load_dotenv()


async def main():
    logger = SKLogger(
        name="SK-Main",
        level=LogLevel.INFO,
        log_to_file=True,
        colorize=True,
    )
    
    logger.section("INITIALIZING SEMANTIC KERNEL", LogLevel.INFO)
    
    kernel = Kernel()

    chat_completion = BedrockChatCompletion(
        model_id=os.getenv("ANTHROPIC_MODEL_ID"),
    )
    kernel.add_service(chat_completion)

    setup_logging()
    logging.getLogger("kernel").setLevel(logging.INFO)

    logger.info("Adding plugins...")
    
    kernel.add_plugin(
        TavilySearchPlugin(os.getenv("TAVILY_API_KEY")),
        plugin_name="TavilyWebSearch",
    )
    logger.info("TavilyWebSearch plugin added")
    
    python_generator = PythonCodeGeneratorPlugin(model_id=os.getenv("ANTHROPIC_MODEL_ID"))
    kernel.add_plugin(python_generator, plugin_name="PythonCodeGenerator")
    logger.info("PythonCodeGenerator plugin added")

    execution_settings = BedrockChatPromptExecutionSettings(
        max_tokens=4096,
        temperature=0.5,
    )
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()

    logger.section("READY FOR USER INTERACTION", LogLevel.INFO)
    
    userInput = None
    while True:
        userInput = input("\033[1m\033[32mUser > \033[0m")

        if userInput == "exit":
            break

        history.add_user_message(userInput)
        
        logger.log_llm_conversation(userInput, "Processing...")

        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )
        
        logger.log_llm_conversation(userInput, str(result))

        print("\033[1m\033[34mAssistant > \033[0m" + str(result))
        history.add_message(result)

if __name__ == "__main__":
    asyncio.run(main())