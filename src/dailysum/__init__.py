"""DailySum - A CLI tool for generating daily work summaries from GitHub activity."""

from .agent import Agent
from .cli import main
from .config import Config

__all__ = ["Agent", "Config", "main"]
