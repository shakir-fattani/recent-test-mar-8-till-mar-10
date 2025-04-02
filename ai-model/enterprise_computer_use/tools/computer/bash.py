import asyncio
import inspect
import os
from typing import Any, ClassVar, Literal

from enterprise_computer_use.tools.base import (
    BaseTool,
    CLIResult,
    ToolError,
    ToolResult,
)


class _BashSession:
    """A session of a bash shell."""

    _started: bool
    _process: asyncio.subprocess.Process

    command: str = "/bin/bash"
    _output_delay: float = 0.2  # seconds
    _timeout: float = 120.0  # seconds
    _sentinel: str = "<<exit>>"

    def __init__(self):
        self._started = False
        self._timed_out = False

    async def start(self):
        if self._started:
            return

        self._process = await asyncio.create_subprocess_shell(
            self.command,
            preexec_fn=os.setsid,
            shell=True,
            bufsize=0,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        self._started = True

    def stop(self):
        """Terminate the bash shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return
        self._process.terminate()

    async def run(self, command: str):
        """Execute a command in the bash shell."""
        if not self._started:
            raise ToolError("Session has not started.")
        if self._process.returncode is not None:
            return ToolResult(
                system="tool must be restarted",
                error=f"bash has exited with returncode {self._process.returncode}",
            )
        if self._timed_out:
            raise ToolError(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted",
            )

        # we know these are not None because we created the process with PIPEs
        assert self._process.stdin
        assert self._process.stdout
        assert self._process.stderr

        # send command to the process
        self._process.stdin.write(
            command.encode() + f"; echo '{self._sentinel}'\n".encode()
        )
        await self._process.stdin.drain()

        # read output from the process, until the sentinel is found
        try:
            async with asyncio.timeout(self._timeout):
                while True:
                    await asyncio.sleep(self._output_delay)
                    # if we read directly from stdout/stderr, it will wait forever for
                    # EOF. use the StreamReader buffer directly instead.
                    output = (
                        self._process.stdout._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
                    )
                    if self._sentinel in output:
                        # strip the sentinel and break
                        output = output[: output.index(self._sentinel)]
                        break
        except asyncio.TimeoutError:
            self._timed_out = True
            raise ToolError(
                f"timed out: bash has not returned in {self._timeout} seconds and must be restarted",
            ) from None

        if output.endswith("\n"):
            output = output[:-1]

        error = (
            self._process.stderr._buffer.decode()  # pyright: ignore[reportAttributeAccessIssue]
        )
        if error.endswith("\n"):
            error = error[:-1]

        # clear the buffers so that the next output can be read correctly
        self._process.stdout._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]
        self._process.stderr._buffer.clear()  # pyright: ignore[reportAttributeAccessIssue]

        return CLIResult(output=output, error=error)


class BashTool(BaseTool):
    """A tool that allows the agent to run bash commands."""

    _session: _BashSession | None

    name: ClassVar[Literal["bash"]] = "bash"
    SUPPORTED_MODELS = {"openai", "claude"}
    # Control whether to include __call__ code in description
    INCLUDE_CALL_IN_DESCRIPTION: ClassVar[bool] = True
    # Properties defining the parameters accepted by __call__ method
    PROPERTIES: ClassVar[dict[str, Any]] = {
        "command": {
            "type": "string",
            "description": "The command to execute.",
        },
        "restart": {
            "type": "boolean",
            "description": "Whether to restart the bash shell.",
        },
    }
    # Required parameters for __call__ method
    REQUIRED: ClassVar[list[str]] = ["command"]

    def __init__(self):
        """Initialize the bash tool."""
        self._session = None
        super().__init__()

    @property
    def code_description(self) -> str:
        """Get the code representation as a string."""
        return inspect.getsource(self.__call__)

    @property
    def description(self) -> str:
        """Get the description from the class's docstring and code."""
        doc = self.__class__.__doc__.strip() if self.__class__.__doc__ else ""

        if self.INCLUDE_CALL_IN_DESCRIPTION:
            return (
                f"{doc}\n\n"
                f"Code implementation:\n"
                f"```python\n{self.code_description}```"
            )
        return doc

    async def __call__(
        self, command: str | None = None, restart: bool = False, **kwargs
    ):
        """Execute a command in the bash shell.

        Args:
            command (str | None, optional): The command to execute. Defaults to
            None.
            restart (bool, optional): Whether to restart the bash shell.
            Defaults to False.

        Raises:
            ToolError: If the command is not provided or the bash shell is not
            running.

        Returns:
            ToolResult: The result of the command execution.
        """
        if restart:
            if self._session:
                self._session.stop()
            self._session = _BashSession()
            await self._session.start()

            return ToolResult(system="tool has been restarted.")

        if self._session is None:
            self._session = _BashSession()
            await self._session.start()

        if command is not None:
            return await self._session.run(command)

        raise ToolError("no command provided.")

    def to_params(self, **kwargs) -> dict[str, Any]:
        """Convert the tool to a function parameter for an LLM.

        Args:
            **kwargs: Keyword arguments.

        Returns:
            dict[str, Any]: The function parameter for an LLM.
        """
        model = kwargs.get("model")

        if model is None:
            raise ValueError("Model must be specified (e.g., 'openai')")

        if model not in self.SUPPORTED_MODELS:
            raise ValueError(
                f"Unsupported model: {model}. "
                f"Supported models are: {self.SUPPORTED_MODELS}"
            )

        # check https://platform.openai.com/docs/guides/function-calling
        if model == "openai":
            return {
                "type": "function",
                "function": {
                    "name": self.name,
                    "description": self.description,
                    "parameters": {
                        "type": "object",
                        "properties": self.PROPERTIES,
                        "required": self.REQUIRED,
                        "additionalProperties": False,
                    },
                    "strict": True,
                },
            }
        elif model == "claude":
            return {
                "name": self.name,
                "description": self.description,
                "input_schema": {
                    "type": "object",
                    "properties": self.PROPERTIES,
                    "required": self.REQUIRED,
                },
            }

        # Add a catch-all return or raise an exception
        raise ValueError(
            f"Model {model} is in SUPPORTED_MODELS but has no implementation"
        )
