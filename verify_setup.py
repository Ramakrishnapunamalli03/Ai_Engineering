"""Run: uv run python verify_setup.py   (or: python verify_setup.py with .venv active)"""
import sys

print(f"Python version: {sys.version}")
assert sys.version_info >= (3, 11), "Need Python 3.11+"

packages = {
    "openai": "openai",
    "anthropic": "anthropic",
    "langchain": "langchain",
    "chromadb": "chromadb",
    "dotenv": "python-dotenv",
    "rich": "rich",
    "pydantic": "pydantic",
    "instructor": "instructor",
}

for import_name, pip_name in packages.items():
    try:
        mod = __import__(import_name)
        version = getattr(mod, "__version__", "✓")
        print(f"  ✅ {pip_name}: {version}")
    except ImportError:
        print(f"  ❌ {pip_name}: NOT INSTALLED — uv add {pip_name}  (or: pip install {pip_name})")

print("\n🎉 Setup complete! You're ready for the course.")