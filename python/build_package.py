import os
import shutil
import subprocess
import sys


def build_package():
    """
    Builds a complete PyPI package and generates wheel/sdist files.
    """
    print("Building Semantic Kernel Tools package...")

    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Clean previous build files
    dist_dir = os.path.join(current_dir, "dist")
    build_dir = os.path.join(current_dir, "build")
    egg_dir = os.path.join(current_dir, "semantic_kernel_plugins.egg-info")

    for dir_path in [dist_dir, build_dir, egg_dir]:
        if os.path.exists(dir_path):
            print(f"Cleaning: {dir_path}")
            shutil.rmtree(dir_path)

    try:
        # Install required packages
        print("Installing build tools...")
        subprocess.check_call(
            [
                sys.executable,
                "-m",
                "pip",
                "install",
                "build",
                "wheel",
                "twine",
                "--upgrade",
            ]
        )

        # Build package (both wheel and sdist)
        print("Building package...")
        subprocess.check_call([sys.executable, "-m", "build", current_dir])

        # List created files
        print("\nGenerated packages:")
        if os.path.exists(dist_dir):
            for file in os.listdir(dist_dir):
                print(f" - {file}")

        print("\nPackage successfully built!")
        print("\nFor local installation:")
        print(f"pip install {os.path.join(dist_dir, '[filename].whl')}")
        print("\nTo upload to PyPI:")
        print("python -m twine upload dist/*")

    except subprocess.CalledProcessError as e:
        print(f"Error during process: {e}")
        sys.exit(1)


def install_package():
    """
    Installs the built package locally.
    """
    print("\nDo you want to install the package locally? (y/n)")
    response = input().lower()

    if response in ["y", "yes"]:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        dist_dir = os.path.join(current_dir, "dist")

        if not os.path.exists(dist_dir):
            print("dist/ directory not found!")
            return

        wheel_files = [f for f in os.listdir(dist_dir) if f.endswith(".whl")]

        if wheel_files:
            wheel_path = os.path.join(dist_dir, wheel_files[0])
            print(f"Installing package: {wheel_files[0]}")

            try:
                subprocess.check_call(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        wheel_path,
                        "--force-reinstall",
                    ]
                )
                print("Package successfully installed!")
                print(
                    "You can now use 'import semantic_kernel_plugins' in any project."
                )
            except subprocess.CalledProcessError as e:
                print(f"Error during installation: {e}")
        else:
            print("No wheel file found!")


if __name__ == "__main__":
    build_package()
    install_package()
