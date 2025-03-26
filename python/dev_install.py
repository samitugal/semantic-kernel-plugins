import os
import subprocess
import sys


def install_package_in_dev_mode():
    print("Installing the package in development mode...")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", current_dir]
        )
        print("Successfully installed the package in development mode.")
        print(
            "Now you can import the package in your notebooks with: import semantic_kernel_plugins"
        )
    except subprocess.CalledProcessError as e:
        print(f"Installation error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    install_package_in_dev_mode()
