import os
import subprocess
import sys


def install_package_in_dev_mode():
    print("Paketi geliştirme modunda yüklüyorum...")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "-e", current_dir]
        )
        print("Kurulum başarılı! Paket geliştirme modunda yüklendi.")
        print(
            "Artık notebooklarda şu şekilde import edebilirsiniz: import semantic_kernel_tools"
        )
    except subprocess.CalledProcessError as e:
        print(f"Kurulum hatası: {e}")
        sys.exit(1)


if __name__ == "__main__":
    install_package_in_dev_mode()
