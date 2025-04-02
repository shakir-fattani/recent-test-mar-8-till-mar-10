"""
Agentic sampling loop that calls the Anthropic API and local implementation of anthropic-defined computer use tools.
"""

import logging
import platform
from collections.abc import Callable
from datetime import datetime
from typing import Any

import httpx

from enterprise_computer_use.agent.agent_factory import AgentFactory
from enterprise_computer_use.constants import APIProvider
from enterprise_computer_use.registry import OSType, ProjectType, Registry
from enterprise_computer_use.tools import ToolResult

COMPUTER_USE_BETA_FLAG = "computer-use-2024-10-22"
PROMPT_CACHING_BETA_FLAG = "prompt-caching-2024-07-31"


PROVIDER_TO_DEFAULT_MODEL_NAME: dict[APIProvider, str] = {
    APIProvider.ANTHROPIC: "claude-3-5-sonnet-20241022",
    APIProvider.BEDROCK: "anthropic.claude-3-5-sonnet-20241022-v2:0",
    APIProvider.VERTEX: "claude-3-5-sonnet-v2@20241022",
    APIProvider.OPENAI: "gpt-4o",
    APIProvider.GEMINI: "gemini-1.5-flash-latest",
}

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
)

# This system prompt is optimized for the Docker environment in this repository and
# specific tool combinations enabled.
# We encourage modifying this system prompt to ensure the model has context for the
# environment it is running in, and to provide any additional information that may be
# helpful for the task at hand.
SYSTEM_PROMPT = f"""<SYSTEM_CAPABILITY>
* You are utilising an Ubuntu virtual machine using {platform.machine()} architecture with internet access.
* You can feel free to install Ubuntu applications with your bash tool. Use curl instead of wget.
* To open firefox, please just click on the firefox icon.  Note, firefox-esr is what is installed on your system.
* Using bash tool you can start GUI applications, but you need to set export DISPLAY=:1 and use a subshell. For example "(DISPLAY=:1 xterm &)". GUI apps run with bash tool will appear within your desktop environment, but they may take some time to appear. Take a screenshot to confirm it did.
* When using your bash tool with commands that are expected to output very large quantities of text, redirect into a tmp file and use str_replace_editor or `grep -n -B <lines before> -A <lines after> <query> <filename>` to confirm output.
* When viewing a page it can be helpful to zoom out so that you can see everything on the page.  Either that, or make sure you scroll down to see everything before deciding something isn't available.
* When using your computer function calls, they take a while to run and send back to you.  Where possible/feasible, try to chain multiple of these calls all into one function calls request.
* The current date is {datetime.today().strftime('%A, %B %-d, %Y')}.
</SYSTEM_CAPABILITY>

<IMPORTANT>
* When using Firefox, if a startup wizard appears, IGNORE IT.  Do not even click "skip this step".  Instead, click on the address bar where it says "Search or enter address", and enter the appropriate search term or URL there.
* If the item you are looking at is a pdf, if after taking a single screenshot of the pdf it seems that you want to read the entire document instead of trying to continue to read the pdf from your screenshots + navigation, determine the URL, use curl to download the pdf, install and use pdftotext to convert it to a text file, and then read that text file directly with your StrReplaceEditTool.
</IMPORTANT>"""


async def sampling_loop(
    *,
    os: OSType,
    project: ProjectType,
    ip_address: str,
    model: str,
    provider: APIProvider,
    system_prompt_suffix: str,
    messages: list[dict[str, Any]],
    output_callback: Callable[[dict[str, Any]], None],  # type: ignore
    tool_output_callback: Callable[[ToolResult, str], None],
    api_response_callback: Callable[
        [httpx.Request, httpx.Response | object | None, Exception | None], None
    ],
    api_key: str,
    only_n_most_recent_images: int | None = None,
    max_tokens: int = 4096,
):
    # Get configuration
    config = Registry.get_config(os, project)

    logging.info("Starting sampling loop with model: %s", model)
    logging.info("OS: %s", os)
    logging.info("Project: %s", project)
    logging.info("tool collection: %s", config.tool_collection)

    # Initialize client instead of environment directly
    env_client = config.client_factory(
        address=ip_address,
        output_callback=output_callback,
        tool_output_callback=tool_output_callback,
    )

    # Create agent
    agent = AgentFactory.get_agent(provider, api_key)
    agent.configure(
        max_tokens=max_tokens,
        model=model,
        api_response_callback=api_response_callback,
        image_truncation=only_n_most_recent_images,
        system_prompt=config.system_prompt + (system_prompt_suffix or ""),
        tool_collection=config.tool_collection,
    )

    # Gym-style interaction loop using client
    obs, _ = await env_client.reset(options={"initial_messages": messages})

    while True:
        # Agent generates action based on observation
        action = agent.predict(obs)

        # Client executes action through gRPC
        obs, _, terminated, truncated, _ = await env_client.step(action)

        if terminated or truncated:
            break

    await env_client.close()
    return obs["messages"]
