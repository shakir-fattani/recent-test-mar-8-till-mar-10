"""
gRPC server for computer use demo
"""

import asyncio
import logging
import os

from enterprise_computer_use.communication.computer_use_server import serve
from enterprise_computer_use.registry import OSType, ProjectType, Registry

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_env_config():
    """Get configuration from environment variables"""
    os_type = os.environ.get("OS")
    project = os.environ.get("PROJECT")

    if not os_type:
        raise ValueError("OS environment variable must be set")
    if not project:
        raise ValueError("PROJECT environment variable must be set")

    if os_type not in [os_type.value for os_type in OSType]:
        raise ValueError(
            f"Invalid OS: {os_type}. Must be one of: "
            f"{[os_type.value for os_type in OSType]}"
        )
    if project not in [proj.value for proj in ProjectType]:
        raise ValueError(
            f"Invalid PROJECT: {project}. Must be one of: "
            f"{[proj.value for proj in ProjectType]}"
        )

    return os_type, project


async def start_grpc_server():
    """Start the gRPC server with the tool collection"""
    try:
        os_type, project = get_env_config()

        # Get configuration based on OS and project
        config = Registry.get_config(OSType(os_type), ProjectType(project))

        logger.info(
            "Starting gRPC server with %s operating system and %s project...",
            os_type,
            project,
        )

        await serve(tool_collection=config.tool_collection)
        logger.info("gRPC server started successfully")

    except Exception as e:
        logger.error("Failed to start gRPC server: %s", e)
        raise


if __name__ == "__main__":
    asyncio.run(start_grpc_server())
