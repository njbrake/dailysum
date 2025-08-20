"""Simple agent for generating daily summaries from GitHub activity."""

from any_agent import AgentConfig, AnyAgent
from any_agent.config import MCPStreamableHttp, Tool

from .config import Config


class Agent:
    """Simple agent that generates daily summaries from GitHub activity."""

    def __init__(self, config: Config) -> None:
        """Initialize the agent with configuration."""
        self.config = config
        self.agent: AnyAgent | None = None

    async def run(self, prompt: str) -> str:
        """Run the agent with a custom prompt and return the summary."""
        if not self.agent:
            await self._create_agent()

        if self.agent is None:
            msg = "Agent not initialized"
            raise RuntimeError(msg)

        result = await self.agent.run_async(prompt)
        return str(result.final_output)

    async def _create_agent(self) -> None:
        """Create and configure the AI agent with GitHub tools."""
        github_tools = [
            "get_me",
            "list_pull_requests", 
            "get_pull_request",
            "list_commits",
            "get_commit",
            "list_branches",
            "list_issues",
            "get_issue",
            "search_repositories",
            "search_issues",
            "search_pull_requests",
            "list_notifications",
            "get_notification_details",
        ]

        tools: list[Tool] = [
            MCPStreamableHttp(
                url="https://api.githubcopilot.com/mcp/",
                headers={"Authorization": f"Bearer {self.config.github_token}"},
                client_session_timeout_seconds=30,
                tools=github_tools,
            ),
        ]

        agent_config = AgentConfig(
            model_id=self.config.model_id,
            tools=tools,
        )

        self.agent = await AnyAgent.create_async("tinyagent", agent_config=agent_config)

    async def cleanup(self) -> None:
        """Clean up MCP connections."""
        if self.agent and hasattr(self.agent, "_mcp_clients"):
            for connection in self.agent._mcp_clients:
                await connection.disconnect()
