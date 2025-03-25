from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="semantic-kernel-tools",
    version="0.1.0",
    author="Sami Tugal",
    author_email="tugalsami@gmail.com",
    description="Ready-to-use plugins and tools for Semantic Kernel",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/samitugal/semantic-kernel-tools",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "semantic-kernel",
        "python-dotenv",
        "tavily-python",
        "anthropic",
        "boto3",
    ],
)
