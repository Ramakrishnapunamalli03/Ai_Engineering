"""
Versioned prompt registry — store, retrieve, and track prompt performance.
"""
import json
from pathlib import Path
from datetime import datetime

class PromptRegistry:
    def __init__(self, storage_dir: str = "prompts"):
        self.dir = Path(storage_dir)
        self.dir.mkdir(exist_ok=True)
    
    def save(self, name: str, template: str, version: str = "1.0", metadata: dict = None):
        """Save a prompt template with version tracking."""
        data = {
            "name": name,
            "version": version,
            "template": template,
            "created_at": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        path = self.dir / f"{name}_v{version}.json"
        path.write_text(json.dumps(data, indent=2))
        print(f"Saved: {path}")
    
    def load(self, name: str, version: str = "1.0") -> str:
        """Load a specific version of a prompt template."""
        path = self.dir / f"{name}_v{version}.json"
        data = json.loads(path.read_text())
        return data["template"]

# Usage
registry = PromptRegistry()
registry.save("summarize", "Summarize in {{style}}: {{text}}", version="1.0")
registry.save("summarize", "As a {{role}}, summarize in {{style}}: {{text}}", version="1.1")
template = registry.load("summarize", version="1.1")