import os
import subprocess
import sys


def check_pypi_config():
    """Checks if PyPI credentials are configured."""
    home = os.path.expanduser("~")
    pypirc_path = os.path.join(home, ".pypirc")

    if not os.path.exists(pypirc_path):
        print("WARNING: ~/.pypirc file not found!")
        print("Save your PyPI credentials in a file with the following format:")
        print("\n[pypi]")
        print("username = your_username")
        print("password = your_password\n")

        print("Do you want to continue? (y/n)")
        response = input().lower()
        if response not in ["y", "yes"]:
            return False

    return True


def publish_to_pypi():
    """Uploads the package to PyPI."""
    print("Publishing Semantic Kernel Tools package to PyPI...")

    if not check_pypi_config():
        print("Operation canceled.")
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    dist_dir = os.path.join(current_dir, "dist")

    if not os.path.exists(dist_dir) or not os.listdir(dist_dir):
        print("No package found to upload! Run build_package.py first.")
        return

    try:
        # Offer Test PyPI upload option
        print("\nDo you want to upload to Test PyPI first? (y/n)")
        response = input().lower()

        if response in ["y", "yes"]:
            print("Uploading to Test PyPI...")
            subprocess.check_call(
                [
                    sys.executable,
                    "-m",
                    "twine",
                    "upload",
                    "--repository-url",
                    "https://test.pypi.org/legacy/",
                    "dist/*",
                ]
            )
            print("Test PyPI upload successful!")
            print("You can install the test package with:")
            print(
                "pip install --index-url https://test.pypi.org/simple/ semantic_kernel_plugins"
            )

        # Real PyPI upload
        print("\nDo you want to proceed with uploading to the real PyPI? (y/n)")
        response = input().lower()

        if response in ["y", "yes"]:
            print("Uploading to PyPI...")
            subprocess.check_call([sys.executable, "-m", "twine", "upload", "dist/*"])
            print("PyPI upload successful!")
            print("The package can now be installed with:")
            print("pip install semantic_kernel_plugins")

    except subprocess.CalledProcessError as e:
        print(f"Error during upload: {e}")
        sys.exit(1)


if __name__ == "__main__":
    publish_to_pypi()
