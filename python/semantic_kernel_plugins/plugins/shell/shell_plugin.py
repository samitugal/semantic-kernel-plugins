import platform
import subprocess
import sys
from typing import List, Optional

from semantic_kernel.functions import kernel_function

from semantic_kernel_plugins.logger.sk_logger import SKLogger


class ShellPlugin:
    def __init__(self):
        self.logger = SKLogger(name="ShellPlugin")
        self.logger.info("SHELL PLUGIN INITIALIZED")
        self.os_type = platform.system().lower()

    @kernel_function(
        description="Execute a shell command",
        name="execute_shell_command",
    )
    def execute_shell_command(self, args: List[str]) -> str:
        """
        Execute a shell command
        Args:
            args: List[str]
        Returns:
            str: The output of the shell command
        """
        try:
            shell = False
            if isinstance(args, str):
                if self.os_type == "windows":
                    shell = True
                else:
                    args = args.split()

            run_args = {
                "capture_output": True,
                "text": True,
                "encoding": "utf-8",
                "errors": "replace",
                "shell": shell,
            }

            self.logger.info(f"Executing shell command: {args}")

            if self.os_type == "windows":
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                run_args["startupinfo"] = startupinfo

            result = subprocess.run(args, **run_args)
            output = result.stdout if result.returncode == 0 else result.stderr
            self.logger.info(f"Command output: {output}")
            return output.strip()

        except Exception as e:
            error_msg = f"Error executing command: {str(e)}"
            self.logger.error(error_msg)
            return error_msg
