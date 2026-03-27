from setuptools import setup, find_packages

setup(
    name="equiti-ai",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "edgartools",
        "beautifulsoup4",
        "requests",
        "pydantic",
        "python-dotenv",
    ],
)
