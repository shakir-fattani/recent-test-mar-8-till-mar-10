"""Factory class for creating different agent instances."""

from typing import Optional

from enterprise_computer_use.agent.abs_agent import AbsAgent
from enterprise_computer_use.agent.claude_agent import (
    BedrockClaudeAgent,
    ClaudeAgent,
    VertexClaudeAgent,
)
from enterprise_computer_use.agent.gemini_agent import GeminiAgent
from enterprise_computer_use.agent.openai_agent import OpenAIAgent
from enterprise_computer_use.constants import APIProvider


class AgentFactory:
    """Factory class for creating agent instances."""

    @staticmethod
    def get_agent(
        agent_type: APIProvider, api_key: Optional[str] = None
    ) -> AbsAgent:
        """Create and return an agent instance based on the specified type.

        Args:
            agent_type: Type of agent to create
            api_key: API key for the agent. Required for ANTHROPIC, OPENAI, and GEMINI.
                    Not used for BEDROCK (uses AWS credentials instead).

        Returns:
            An instance of the specified agent type

        Raises:
            ValueError: If an invalid agent type is specified or if api_key is missing when required
        """
        agent_map = {
            APIProvider.OPENAI: OpenAIAgent,
            APIProvider.ANTHROPIC: ClaudeAgent,
            APIProvider.GEMINI: GeminiAgent,
            APIProvider.BEDROCK: BedrockClaudeAgent,
            APIProvider.VERTEX: VertexClaudeAgent,
        }

        if agent_type not in agent_map:
            raise ValueError(
                f"Invalid agent type: {agent_type}. "
                f"Valid types are: {', '.join(agent_map.keys())}"
            )

        # Check if API key is required for this provider
        api_key_required = agent_type in {
            APIProvider.ANTHROPIC,
            APIProvider.OPENAI,
            APIProvider.GEMINI,
        }

        if api_key_required and not api_key:
            raise ValueError(f"API key is required for {agent_type} provider")

        # Only pass api_key if the provider needs it
        kwargs = {"api_key": api_key} if api_key_required else {}

        return agent_map[agent_type](**kwargs)
