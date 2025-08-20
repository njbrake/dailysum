# DailySum

A simple CLI tool that uses AI agents to generate daily work summaries from your GitHub activity.

## Quick Start

1. Install: `pip install dailysum`
2. Configure: `dailysum init`
3. Generate: `dailysum generate`

## Features

- Simple agent-based approach for generating daily summaries
- Easy configuration with GitHub token
- Analyzes PRs, issues, commits, and reviews
- Supports multiple LLM providers (OpenAI, Anthropic, Mistral, Google, etc.)
- Powered by Mozilla AI's any-agent framework

## How It Works

Uses a simple agent powered by Mozilla AI's [any-agent](https://github.com/njbrake/any-agent) framework with [any-llm](https://github.com/njbrake/any-llm) for LLM provider abstraction. The agent connects to GitHub via Model Context Protocol (MCP) to analyze your activity and generate summaries.
