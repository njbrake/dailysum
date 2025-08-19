"""Command-line interface for What Did You Do Today."""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .config import Config
from .github_summarizer import GitHubSummarizer

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli():
    """What Did You Do Today - Generate daily work summaries from GitHub activity.

    This tool uses AI agents powered by any-llm and any-agent to analyze your
    GitHub activity and generate professional daily status updates.
    """
    pass


@cli.command()
@click.option("--github-token", prompt="GitHub Token", hide_input=True, help="Your GitHub personal access token")
@click.option(
    "--model-id", default="openai/gpt-4o-mini", help="Model to use for summarization (default: openai/gpt-4o-mini)"
)
@click.option("--company", help="Your company name (optional)")
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    help="Path to save config file (default: ~/.config/what-did-you-do-today/config.toml)",
)
def init(github_token: str, model_id: str, company: Optional[str], config_path: Optional[Path]):
    """Initialize configuration for What Did You Do Today."""
    config = Config(github_token=github_token, model_id=model_id, company=company)

    try:
        config.save_to_file(config_path)
        config_file_path = config_path or Path.home() / ".config" / "what-did-you-do-today" / "config.toml"
        console.print(f"✅ Configuration saved to {config_file_path}", style="green")
        console.print(
            "\n💡 You can now run 'what-did-you-do-today generate' to create your daily summary!", style="blue"
        )
    except Exception as e:
        console.print(f"❌ Error saving configuration: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    help="Path to config file (default: ~/.config/what-did-you-do-today/config.toml)",
)
@click.option("--use-env", is_flag=True, help="Use environment variables instead of config file")
@click.option("--evaluate", is_flag=True, help="Evaluate the generated summary for quality")
def generate(config_path: Optional[Path], use_env: bool, evaluate: bool):
    """Generate a daily work summary from your GitHub activity."""

    try:
        if use_env:
            config = Config.from_env()
        else:
            config = Config.from_file(config_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"❌ Configuration error: {e}", style="red")
        console.print("💡 Run 'what-did-you-do-today init' to set up your configuration.", style="blue")
        sys.exit(1)

    async def _generate():
        summarizer = GitHubSummarizer(config)

        try:
            with console.status("[bold green]Analyzing your GitHub activity..."):
                summary = await summarizer.generate_summary()

            console.print("\n" + "=" * 60)
            console.print(
                Panel(
                    Text(summary, style="white"), title="📋 Your Daily Summary", title_align="left", border_style="blue"
                )
            )

            if evaluate:
                with console.status("[bold yellow]Evaluating summary quality..."):
                    # We need the full result object for evaluation, not just the summary text
                    # This is a simplified version - in practice you'd want to store the result
                    console.print("\n💡 Evaluation feature requires storing the full agent result.", style="yellow")

        except Exception as e:
            console.print(f"❌ Error generating summary: {e}", style="red")
            sys.exit(1)
        finally:
            await summarizer.cleanup()

    try:
        asyncio.run(_generate())
    except KeyboardInterrupt:
        console.print("\n❌ Operation cancelled by user.", style="red")
        sys.exit(1)


@cli.command()
@click.option("--config-path", type=click.Path(path_type=Path), help="Path to config file to display")
def config(config_path: Optional[Path]):
    """Display current configuration."""
    try:
        config = Config.from_file(config_path)
        config_file_path = config_path or Path.home() / ".config" / "what-did-you-do-today" / "config.toml"

        console.print(f"\n📁 Configuration from: {config_file_path}")
        console.print(
            Panel(
                f"Model: {config.model_id}\n"
                f"Company: {config.company or 'Not set'}\n"
                f"GitHub Token: {'*' * (len(config.github_token) - 4) + config.github_token[-4:]}",
                title="⚙️  Current Configuration",
                border_style="blue",
            )
        )
    except FileNotFoundError as e:
        console.print(f"❌ {e}", style="red")
        sys.exit(1)


def main():
    """Main entry point for the CLI."""
    cli()


if __name__ == "__main__":
    main()
