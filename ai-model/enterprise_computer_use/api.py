from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import asyncio
import os
import sys
from anthropic.types.beta import BetaTextBlockParam, BetaToolResultBlockParam


# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from enterprise_computer_use.loop import sampling_loop
from enterprise_computer_use.registry import OSType, ProjectType
from enterprise_computer_use.constants import APIProvider
from enterprise_computer_use.tools import ToolResult

app = FastAPI()

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]

# Initialize session state
session_state = {
    "messages": [],
    "os": os.getenv("OS", "linux"),
    "project": os.getenv("PROJECT", "claude_computer_use"),
    "api_key": os.getenv("ANTHROPIC_API_KEY", "default_project"),
    "provider": APIProvider.ANTHROPIC,
    "model": "default_model",
    "custom_system_prompt": "",
    "only_n_most_recent_images": 3,
    "tools": {},
    "responses": {},
}

@app.get("/chat")
async def chat():
    # Run the agent sampling loop with the newest message
    session_state["messages"] = await sampling_loop(
        os=OSType(session_state["os"]),
        project=ProjectType(session_state["project"]),
        ip_address="localhost",
        system_prompt_suffix=session_state["custom_system_prompt"],
        model=session_state["model"],
        provider=session_state["provider"],
        messages=session_state["messages"],
        output_callback=lambda sender, message: None,  # No-op for API
        tool_output_callback=lambda tool_output, tool_id: None,  # No-op for API
        api_response_callback=lambda request, response, error: None,  # No-op for API
        api_key=session_state["api_key"],  # Replace with your actual API key
        only_n_most_recent_images=session_state["only_n_most_recent_images"],
    )

    return {"messages": session_state["messages"]}

@app.post("/chat")
async def chat(request: ChatRequest):
    # Add new messages to session state
    for message in request.messages:
        session_state["messages"].append(
            {
                "role": message.role,
                "content": [
                    BetaTextBlockParam(type="text", text=message.content),
                ],
            }
        )

    # Run the agent sampling loop with the newest message
    session_state["messages"] = await sampling_loop(
        os=OSType(session_state["os"]),
        project=ProjectType(session_state["project"]),
        ip_address="localhost",
        system_prompt_suffix=session_state["custom_system_prompt"],
        model=session_state["model"],
        provider=session_state["provider"],
        messages=session_state["messages"],
        output_callback=lambda sender, message: None,  # No-op for API
        tool_output_callback=lambda tool_output, tool_id: None,  # No-op for API
        api_response_callback=lambda request, response, error: None,  # No-op for API
        api_key=session_state["api_key"],  # Replace with your actual API key
        only_n_most_recent_images=session_state["only_n_most_recent_images"],
    )

    return {"messages": session_state["messages"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)