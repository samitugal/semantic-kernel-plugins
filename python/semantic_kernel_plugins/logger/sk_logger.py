import logging
import os
import sys
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


class LogLevel(Enum):
    DEBUG = (10, "\033[36m")
    INFO = (20, "\033[32m")
    WARN = (30, "\033[33m")
    ERROR = (40, "\033[31m")
    CRITICAL = (50, "\033[35m")

    LLM_THINKING = (15, "\033[38;5;135m")
    LLM_PLANNING = (16, "\033[38;5;39m")
    LLM_CODE = (17, "\033[38;5;208m")
    LLM_EXECUTION = (18, "\033[38;5;34m")

    def __init__(self, level_num, color_code):
        self.level_num = level_num
        self.color_code = color_code


class SKLogger:
    """
    Logger class for Semantic-Kernel-Plugins
    """

    RESET = "\033[0m"
    BOLD = "\033[1m"

    ASCII_EMOJI_MAP = {
        "🧠": "[BRAIN]",
        "❌": "[X]",
        "✅": "[OK]",
        "📋": "[DOC]",
        "🔍": "[SEARCH]",
        "👤": "[USER]",
        "🤖": "[AI]",
        "🌐": "[WEB]",
    }

    def __init__(
        self,
        name: str = "SK-Logger",
        level: LogLevel = LogLevel.INFO,
        log_to_file: bool = True,
        log_dir: str = "logs",
        colorize: bool = True,
        max_line_length: int = 120,
        include_timestamp: bool = True,
        use_ascii_emoji: bool = None,
    ):
        self.name = name
        self.level = level
        self.log_to_file = log_to_file
        self.log_dir = log_dir
        self.colorize = colorize
        self.max_line_length = max_line_length
        self.include_timestamp = include_timestamp

        if use_ascii_emoji is None:
            self.use_ascii_emoji = sys.platform == "win32"
        else:
            self.use_ascii_emoji = use_ascii_emoji

        if sys.platform == "win32":
            try:
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleOutputCP(65001)

                import io

                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
            except:
                self.use_ascii_emoji = True

        for log_level in LogLevel:
            logging.addLevelName(log_level.level_num, log_level.name)

        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)

        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(self.level.level_num)

        self.formatter = logging.Formatter("%(message)s")
        self.console_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.console_handler)

        if log_to_file:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            log_filename = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(
                os.path.join(log_dir, log_filename), mode="w", encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)

            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s"
            )
            file_handler.setFormatter(file_formatter)

            self.logger.addHandler(file_handler)

        self.message_buffer = []
        self.max_buffer_size = 1000

    def _replace_emojis(self, text: str) -> str:
        """Change emojis to ascii characters"""
        if not self.use_ascii_emoji:
            return text

        for emoji, ascii_ver in self.ASCII_EMOJI_MAP.items():
            text = text.replace(emoji, ascii_ver)
        return text

    def _format_message(self, level: LogLevel, message: str) -> str:
        """Colorize and format message"""
        message = self._replace_emojis(message)

        timestamp = (
            f"[{datetime.now().strftime('%H:%M:%S.%f')[:-3]}] "
            if self.include_timestamp
            else ""
        )
        level_name = f"[{level.name}] "

        if self.colorize:
            level_name = f"{level.color_code}{level_name}{self.RESET}"

        return f"{timestamp}{level_name}{message}"

    def _log(self, level: LogLevel, message: str, **kwargs):
        """General log function"""
        if level.level_num < self.level.level_num:
            return

        formatted_message = self._format_message(level, message)

        try:
            self.logger.log(level.level_num, formatted_message)
        except UnicodeEncodeError:
            formatted_message = self._format_message(
                level, self._replace_emojis(message)
            )
            self.logger.log(level.level_num, formatted_message)

        self.message_buffer.append((level, message, time.time()))
        if len(self.message_buffer) > self.max_buffer_size:
            self.message_buffer.pop(0)

    def debug(self, message: str, **kwargs):
        self._log(LogLevel.DEBUG, message, **kwargs)

    def info(self, message: str, **kwargs):
        self._log(LogLevel.INFO, message, **kwargs)

    def warn(self, message: str, **kwargs):
        self._log(LogLevel.WARN, message, **kwargs)

    def error(self, message: str, **kwargs):
        self._log(LogLevel.ERROR, message, **kwargs)

    def critical(self, message: str, **kwargs):
        self._log(LogLevel.CRITICAL, message, **kwargs)

    def llm_thinking(self, message: str, **kwargs):
        """Log LLM's thinking process"""
        self._log(LogLevel.LLM_THINKING, message, **kwargs)

    def llm_planning(self, message: str, **kwargs):
        """Log LLM's planning process"""
        self._log(LogLevel.LLM_PLANNING, message, **kwargs)

    def llm_code(self, code: str, language: str = "python", **kwargs):
        """Log LLM's generated code"""
        header = f"🧠 Generated {language.upper()} code:"
        formatted_code = f"\n```{language}\n{code}\n```\n"
        self._log(LogLevel.LLM_CODE, f"{header}{formatted_code}", **kwargs)

    def llm_execution(self, result: str, success: bool = True, **kwargs):
        """Log LLM's code execution result"""
        status = "✅ Execution succeeded:" if success else "❌ Execution failed:"
        self._log(LogLevel.LLM_EXECUTION, f"{status}\n{result}", **kwargs)

    def section(self, title: str, level: LogLevel = LogLevel.INFO):
        """Create a distinct section header"""
        line = "=" * min(len(title) + 4, self.max_line_length)
        self._log(level, f"\n{line}")
        self._log(level, f"  {title}")
        self._log(level, f"{line}\n")

    def get_recent_logs(
        self, count: int = 10, level: Optional[LogLevel] = None
    ) -> List[Tuple[LogLevel, str, float]]:
        """Get recent logs, optionally filtered by a specific level"""
        if level is None:
            return self.message_buffer[-count:]

        return [log for log in self.message_buffer if log[0] == level][-count:]

    def log_llm_conversation(self, prompt: str, response: str):
        """Log LLM conversation between user and AI"""
        self.section("LLM CONVERSATION")
        self._log(LogLevel.INFO, f"👤 User: {prompt}")
        self._log(LogLevel.LLM_THINKING, f"🤖 AI: {response}")

    def log_code_generation_process(
        self,
        request: str,
        planning: str,
        code: str,
        execution_result: str,
        success: bool = True,
    ):
        """Log the entire code generation process"""
        self.section("CODE GENERATION PROCESS")
        self._log(LogLevel.INFO, f"📋 Request: {request}")
        self.llm_planning(f"🔍 Planning:\n{planning}")
        self.llm_code(code)
        self.llm_execution(execution_result, success)

    def log_search_results(self, query: str, results: list, success: bool = True):
        """
        Log web search results from Tavily

        Args:
            query: Search query string
            results: List of search results
            success: Whether the search was successful
        """
        self.section("WEB SEARCH RESULTS")
        self._log(LogLevel.INFO, f"🔍 Query: {query}")

        if not success:
            self._log(LogLevel.ERROR, "❌ Search failed")
            return

        for idx, result in enumerate(results, 1):
            title = result.get("title", "No title")
            url = result.get("url", "No URL")
            snippet = result.get("snippet", "No snippet available")

            self._log(LogLevel.INFO, f"\n🌐 Result {idx}:")
            self._log(LogLevel.INFO, f"Title: {title}")
            self._log(LogLevel.INFO, f"URL: {url}")
            self._log(LogLevel.INFO, f"Summary: {snippet}")
            self._log(LogLevel.INFO, "-" * 80)
