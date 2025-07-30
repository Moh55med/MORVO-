from setuptools import setup, find_packages

setup(
    name="morvo_python",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fastapi",
        "uvicorn",
        "aiohttp",
        "python-dotenv",
        "pydantic",
        "langgraph",
        "typing-extensions",
        "httpx",
        "supabase",
    ],
)