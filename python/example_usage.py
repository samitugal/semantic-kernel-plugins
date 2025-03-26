import asyncio
import logging
import os

from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.bedrock import BedrockChatCompletion
from semantic_kernel.connectors.ai.bedrock.bedrock_prompt_execution_settings import \
    BedrockChatPromptExecutionSettings
from semantic_kernel.connectors.ai.function_choice_behavior import \
    FunctionChoiceBehavior
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.utils.logging import setup_logging

from semantic_kernel_plugins.plugins.python.python_code_generator import \
    PythonCodeGeneratorPlugin
from semantic_kernel_plugins.plugins.web.tavily_web_search import \
    TavilySearchPlugin

load_dotenv()


async def main():
    kernel = Kernel()

    chat_completion = BedrockChatCompletion(
        model_id=os.getenv("ANTHROPIC_MODEL_ID"),
    )
    kernel.add_service(chat_completion)

    setup_logging()
    logging.getLogger("kernel").setLevel(logging.INFO)

    ## Ready to use plugins - Tavily Web Search
    kernel.add_plugin(
        TavilySearchPlugin(os.getenv("TAVILY_API_KEY")),
        plugin_name="TavilyWebSearch",
    )

    ## Ready to use plugins - Python Code Generator
    execution_settings = BedrockChatPromptExecutionSettings(
        max_tokens=4096,
        temperature=0.5,
    )
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    python_generator = PythonCodeGeneratorPlugin(
        chat_service=chat_completion, execution_settings=execution_settings
    )
    kernel.add_plugin(python_generator, plugin_name="PythonCodeGenerator")

    history = ChatHistory()
    userInput = None
    while True:
        userInput = input("\033[1m\033[32mUser > \033[0m")

        if userInput == "exit":
            break

        history.add_user_message(userInput)
        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )
        print("\033[1m\033[34mAssistant > \033[0m" + str(result))
        history.add_message(result)


if __name__ == "__main__":
    asyncio.run(main())
