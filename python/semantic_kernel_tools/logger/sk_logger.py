import logging
import os
import sys
import time
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, Union


class LogLevel(Enum):
    DEBUG = (10, "\033[36m")  # Cyan
    INFO = (20, "\033[32m")  # Green
    WARN = (30, "\033[33m")  # Yellow
    ERROR = (40, "\033[31m")  # Red
    CRITICAL = (50, "\033[35m")  # Magenta

    LLM_THINKING = (15, "\033[38;5;135m")  # Light Purple
    LLM_PLANNING = (16, "\033[38;5;39m")  # Light Blue
    LLM_CODE = (17, "\033[38;5;208m")  # Orange
    LLM_EXECUTION = (18, "\033[38;5;34m")  # Light Green

    def __init__(self, level_num, color_code):
        self.level_num = level_num
        self.color_code = color_code


class SKLogger:
    """Semantic Kernel için renkli ve detaylı logger sınıfı"""

    RESET = "\033[0m"
    BOLD = "\033[1m"

    # Emoji alternatifler (ASCII karakterler)
    ASCII_EMOJI_MAP = {
        "🧠": "[BRAIN]",  # Beyin
        "❌": "[X]",  # Çarpı
        "✅": "[OK]",  # Onay
        "📋": "[DOC]",  # Dokuman
        "🔍": "[SEARCH]",  # Arama
        "👤": "[USER]",  # Kullanıcı
        "🤖": "[AI]",  # Robot
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

        # Windows ise veya kullanıcı açıkça belirtmişse emoji yerine ASCII kullan
        if use_ascii_emoji is None:
            self.use_ascii_emoji = sys.platform == "win32"
        else:
            self.use_ascii_emoji = use_ascii_emoji

        # Windows'ta UTF-8 kodlamasını etkinleştirmeyi dene
        if sys.platform == "win32":
            try:
                # Windows'ta çıktı akışını UTF-8'e ayarla
                import ctypes

                kernel32 = ctypes.windll.kernel32
                kernel32.SetConsoleOutputCP(65001)  # UTF-8 kod sayfası

                # Python 3.7+'da PYTHONIOENCODING ayarını zorla
                import io

                sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")
                sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8")
            except:
                # UTF-8 ayarı başarısız olduysa ASCII emojilerini kullan
                self.use_ascii_emoji = True

        # Custom log levels ekleme
        for log_level in LogLevel:
            logging.addLevelName(log_level.level_num, log_level.name)

        # Logger oluşturma
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)  # Her şeyi loglayacağız

        # Console handler oluşturma
        self.console_handler = logging.StreamHandler(sys.stdout)
        self.console_handler.setLevel(self.level.level_num)

        # Basit formatter
        self.formatter = logging.Formatter("%(message)s")
        self.console_handler.setFormatter(self.formatter)

        self.logger.addHandler(self.console_handler)

        # Dosya loglama
        if log_to_file:
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)

            log_filename = f"{self.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            file_handler = logging.FileHandler(
                os.path.join(log_dir, log_filename), mode="w", encoding="utf-8"
            )
            file_handler.setLevel(logging.DEBUG)

            # Dosyada renkli kodlar olmadan logla
            file_formatter = logging.Formatter(
                "%(asctime)s - %(name)s:%(lineno)d - %(levelname)s] %(message)s"
            )
            file_handler.setFormatter(file_formatter)

            self.logger.addHandler(file_handler)

        # Son mesajları tutan buffer
        self.message_buffer = []
        self.max_buffer_size = 1000

    def _replace_emojis(self, text: str) -> str:
        """Emojileri ASCII karşılıklarıyla değiştir"""
        if not self.use_ascii_emoji:
            return text

        for emoji, ascii_ver in self.ASCII_EMOJI_MAP.items():
            text = text.replace(emoji, ascii_ver)
        return text

    def _format_message(self, level: LogLevel, message: str) -> str:
        """Mesajı renklendirme ve format ekleme"""
        # Önce emojileri değiştir
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
        """Genel log fonksiyonu"""
        if level.level_num < self.level.level_num:
            return

        formatted_message = self._format_message(level, message)

        try:
            self.logger.log(level.level_num, formatted_message)
        except UnicodeEncodeError:
            # Unicode hatası durumunda emojileri zorla değiştir ve tekrar dene
            formatted_message = self._format_message(
                level, self._replace_emojis(message)
            )
            self.logger.log(level.level_num, formatted_message)

        # Buffer'a ekle
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
        """LLM'in düşünme sürecini logla"""
        self._log(LogLevel.LLM_THINKING, message, **kwargs)

    def llm_planning(self, message: str, **kwargs):
        """LLM'in planlama sürecini logla"""
        self._log(LogLevel.LLM_PLANNING, message, **kwargs)

    def llm_code(self, code: str, language: str = "python", **kwargs):
        """LLM'in ürettiği kodu logla"""
        header = f"🧠 Generated {language.upper()} code:"
        formatted_code = f"\n```{language}\n{code}\n```\n"
        self._log(LogLevel.LLM_CODE, f"{header}{formatted_code}", **kwargs)

    def llm_execution(self, result: str, success: bool = True, **kwargs):
        """LLM'in kod yürütme sonucunu logla"""
        status = "✅ Execution succeeded:" if success else "❌ Execution failed:"
        self._log(LogLevel.LLM_EXECUTION, f"{status}\n{result}", **kwargs)

    def section(self, title: str, level: LogLevel = LogLevel.INFO):
        """Belirgin bir bölüm başlığı oluştur"""
        line = "=" * min(len(title) + 4, self.max_line_length)
        self._log(level, f"\n{line}")
        self._log(level, f"  {title}")
        self._log(level, f"{line}\n")

    def get_recent_logs(
        self, count: int = 10, level: Optional[LogLevel] = None
    ) -> List[Tuple[LogLevel, str, float]]:
        """Son logları getir, isteğe bağlı olarak belirli bir seviyeye filtrele"""
        if level is None:
            return self.message_buffer[-count:]

        return [log for log in self.message_buffer if log[0] == level][-count:]

    def log_llm_conversation(self, prompt: str, response: str):
        """Kullanıcı ve LLM arasındaki konuşmayı logla"""
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
        """Kod üretim sürecinin tamamını logla"""
        self.section("CODE GENERATION PROCESS")
        self._log(LogLevel.INFO, f"📋 Request: {request}")
        self.llm_planning(f"🔍 Planning:\n{planning}")
        self.llm_code(code)
        self.llm_execution(execution_result, success)
