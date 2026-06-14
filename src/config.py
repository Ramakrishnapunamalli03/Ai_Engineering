"""
Centralized configuration with validation.
Usage: from config import settings
"""
import os
from dataclasses import dataclass, field
from dotenv import load_dotenv

load_dotenv()  # Load .env file


@dataclass
class Settings:
    """App settings loaded from environment variables."""
    
    # Required keys (will raise if missing)
    openai_api_key: str = field(default_factory=lambda: os.environ["OPENAI_API_KEY"])
    
    # Optional keys (None if not set)
    anthropic_api_key: str | None = field(
        default_factory=lambda: os.getenv("ANTHROPIC_API_KEY")
    )
    google_api_key: str | None = field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY")
    )
    
    # App config with defaults
    default_model: str = field(
        default_factory=lambda: os.getenv("DEFAULT_MODEL", "gpt-4o-mini")
    )
    max_tokens: int = field(
        default_factory=lambda: int(os.getenv("MAX_TOKENS", "4096"))
    )
    log_level: str = field(
        default_factory=lambda: os.getenv("LOG_LEVEL", "info")
    )
    
    def __post_init__(self):
        """Validate keys have the expected format."""
        if not self.openai_api_key.startswith("sk-"):
            raise ValueError("OPENAI_API_KEY should start with 'sk-'")
        
        if self.anthropic_api_key and not self.anthropic_api_key.startswith("sk-ant"):
            raise ValueError("ANTHROPIC_API_KEY should start with 'sk-ant'")

    def available_providers(self) -> list[str]:
        """Return list of configured providers."""
        providers = ["openai"]  # Always available (required)
        if self.anthropic_api_key:
            providers.append("anthropic")
        if self.google_api_key:
            providers.append("google")
        return providers


# Singleton instance — import this everywhere
settings = Settings()
print(f"✅ Config loaded | Providers: {settings.available_providers()}")
print(f"   Default model: {settings.default_model}")