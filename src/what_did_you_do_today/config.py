"""Configuration management for What Did You Do Today."""

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Optional

import toml


@dataclass
class Config:
    """Configuration for the GitHub summarizer."""
    
    github_token: str
    model_id: str = "openai/gpt-4o-mini"
    company: Optional[str] = None
    
    @classmethod
    def from_file(cls, config_path: Optional[Path] = None) -> "Config":
        """Load configuration from a TOML file."""
        if config_path is None:
            config_path = Path.home() / ".config" / "what-did-you-do-today" / "config.toml"
        
        if not config_path.exists():
            raise FileNotFoundError(
                f"Configuration file not found at {config_path}. "
                f"Run 'what-did-you-do-today init' to create one."
            )
        
        config_data = toml.load(config_path)
        return cls(**config_data)
    
    @classmethod
    def from_env(cls) -> "Config":
        """Load configuration from environment variables."""
        github_token = os.getenv("GITHUB_TOKEN") or os.getenv("GITHUB_PAT")
        if not github_token:
            raise ValueError(
                "GitHub token not found. Set GITHUB_TOKEN or GITHUB_PAT environment variable, "
                "or run 'what-did-you-do-today init' to create a config file."
            )
        
        return cls(
            github_token=github_token,
            model_id=os.getenv("MODEL_ID", "openai/gpt-4o-mini"),
            company=os.getenv("COMPANY"),
        )
    
    def save_to_file(self, config_path: Optional[Path] = None) -> None:
        """Save configuration to a TOML file."""
        if config_path is None:
            config_path = Path.home() / ".config" / "what-did-you-do-today" / "config.toml"
        
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        config_data = {
            "github_token": self.github_token,
            "model_id": self.model_id,
        }
        if self.company:
            config_data["company"] = self.company
        
        with open(config_path, "w") as f:
            toml.dump(config_data, f)
