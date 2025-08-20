"""Command-line interface for DailySum."""

import asyncio
import sys
from pathlib import Path

import click
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .agent import Agent
from .config import Config

console = Console()


@click.group()
@click.version_option(version="0.1.0")
def cli() -> None:
    """Generate daily work summaries from GitHub activity.

    This tool uses AI agents powered by any-llm and any-agent to analyze your
    GitHub activity and generate professional daily status updates.
    """


@cli.command()
@click.option("--github-token", prompt="GitHub Token", hide_input=True, help="Your GitHub personal access token")
@click.option(
    "--model-id", default="openai/gpt-4o-mini", help="Model to use for summarization (default: openai/gpt-4o-mini)"
)
@click.option("--company", help="Your company name (optional)")
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    help="Path to save config file (default: ~/.config/dailysum/config.toml)",
)
def init(github_token: str, model_id: str, company: str | None, config_path: Path | None) -> None:
    """Initialize configuration for DailySum."""
    cfg = Config(github_token=github_token, model_id=model_id, company=company)

    try:
        cfg.save_to_file(config_path)
        config_file_path = config_path or Path.home() / ".config" / "dailysum" / "config.toml"
        console.print(f"✅ Configuration saved to {config_file_path}", style="green")
        console.print("\n💡 You can now run 'dailysum generate' to create your daily summary!", style="blue")
    except Exception as e:
        console.print(f"❌ Error saving configuration: {e}", style="red")
        sys.exit(1)


@cli.command()
@click.option(
    "--config-path",
    type=click.Path(path_type=Path),
    help="Path to config file (default: ~/.config/dailysum/config.toml)",
)
@click.option("--use-env", is_flag=True, help="Use environment variables instead of config file")
def generate(config_path: Path | None, use_env: bool) -> None:
    """Generate a daily work summary from your GitHub activity."""
    try:
        if use_env:
            config = Config.from_env()
        else:
            config = Config.from_file(config_path)
    except (FileNotFoundError, ValueError) as e:
        console.print(f"❌ Configuration error: {e}", style="red")
        console.print("💡 Run 'dailysum init' to set up your configuration.", style="blue")
        sys.exit(1)

    def _get_default_prompt(cfg: Config) -> str:
        """Get the default prompt for daily summary generation."""
        company_context = f" at {cfg.company}" if cfg.company else ""

        return f"""I'm a software engineer{company_context}, and I do most of my work on GitHub.
I need to provide a daily update about what I did yesterday and what I plan to do today.
Please help me compile this info and output it in the following format:

```
Yesterday:
- (List of PRs opened/closed/reviewed, issues worked on, commits made)
Today:
- (List of things it looks like I'll be working on based on recent activity)
```

Please be concise and focus on the most important work items."""

    async def _generate() -> None:
        agent = Agent(config)

        try:
            prompt = _get_default_prompt(config)

            with console.status("[bold green]Analyzing your GitHub activity..."):
                summary = await agent.run(prompt)

            console.print("\n" + "=" * 60)
            console.print(
                Panel(
                    Text(summary, style="white"),
                    title="📋 Your Daily Summary",
                    title_align="left",
                    border_style="blue"
                )
            )

        except Exception as e:
            console.print(f"❌ Error generating summary: {e}", style="red")
            sys.exit(1)
        finally:
            await agent.cleanup()

    try:
        asyncio.run(_generate())
    except KeyboardInterrupt:
        console.print("\n❌ Operation cancelled by user.", style="red")
        sys.exit(1)


@cli.command()
@click.option("--config-path", type=click.Path(path_type=Path), help="Path to config file to display")
def show_config(config_path: Path | None) -> None:
    """Display current configuration."""
    try:
        cfg = Config.from_file(config_path)
        config_file_path = config_path or Path.home() / ".config" / "dailysum" / "config.toml"

        console.print(f"\n📁 Configuration from: {config_file_path}")
        console.print(
            Panel(
                f"Model: {cfg.model_id}\n"
                f"Company: {cfg.company or 'Not set'}\n"
                f"GitHub Token: {'*' * (len(cfg.github_token) - 4) + cfg.github_token[-4:]}",
                title="⚙️  Current Configuration",
                border_style="blue",
            )
        )
    except FileNotFoundError as e:
        console.print(f"❌ {e}", style="red")
        sys.exit(1)


def main() -> None:
    """Run the CLI application."""
    cli()


if __name__ == "__main__":
    main()
