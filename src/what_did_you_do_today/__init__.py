"""What Did You Do Today - A CLI tool for generating daily work summaries from GitHub activity."""

__version__ = "0.1.0"
__author__ = "Mozilla AI"
__description__ = "A CLI tool that uses AI agents to generate daily work summaries from GitHub activity"

from .cli import main
from .config import Config
from .github_summarizer import GitHubSummarizer

__all__ = ["main", "Config", "GitHubSummarizer"]
