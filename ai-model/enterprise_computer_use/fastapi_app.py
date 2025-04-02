"""
Entrypoint for FastAPI, see https://fastapi.tiangolo.com/
"""

import os
import sys
from typing import cast
import traceback
from datetime import datetime
from pathlib import PosixPath
from typing import Dict, List, Optional, Union, Any
from contextlib import contextmanager
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field

# Add the project root to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from enterprise_computer_use.constants import APIProvider
from enterprise_computer_use.loop import PROVIDER_TO_DEFAULT_MODEL_NAME, sampling_loop
from enterprise_computer_use.registry import OSType, ProjectType
from enterprise_computer_use.tools import ToolResult

app = FastAPI(title="Cambio AI Agent")
templates = Jinja2Templates(directory="templates")

CONFIG_DIR = PosixPath("~/.anthropic").expanduser()
API_KEY_FILE = CONFIG_DIR / "api_key"

# Models for API
class ContentBlock(BaseModel):
    type: str
    text: Optional[str] = None
    id: Optional[str] = None
    name: Optional[str] = None
    input: Optional[Any] = None
    source: Optional[Dict] = None
    tool_use_id: Optional[str] = None
    content: Optional[str] = None
    is_error: Optional[bool] = None

class Message(BaseModel):
    role: str
    isNew: Optional[bool] = False
    content: Union[str, List[ContentBlock]]
    def to_dict(self) -> Dict[str, str]:
        return {
            "role": self.role,
            "content": self.content
        }

class StateModel(BaseModel):
    ip_address: str = Field(default_factory=lambda: os.getenv("IP_ADDRESS", "localhost"))
    messages: List[Message] = []
    api_keys: Dict[str, str] = Field(default_factory=lambda: {
        APIProvider.ANTHROPIC: os.getenv("ANTHROPIC_API_KEY", ""),
        APIProvider.OPENAI: os.getenv("OPENAI_API_KEY", ""),
        APIProvider.GEMINI: os.getenv("GOOGLE_API_KEY", ""),
        APIProvider.BEDROCK: "",
        APIProvider.VERTEX: "",
    })
    provider: str = APIProvider.ANTHROPIC
    model: str = PROVIDER_TO_DEFAULT_MODEL_NAME[APIProvider.ANTHROPIC]
    auth_validated: bool = False
    responses: Dict[str, Any] = {}
    tools: Dict[str, Any] = {}
    only_n_most_recent_images: int = 3
    custom_system_prompt: str = ""
    hide_images: bool = False
    in_sampling_loop: bool = False
    os: str = ""
    project: str = ""

class MessageRequest(BaseModel):
    messages: List[Message]

# Global state
state = StateModel()

# Load environment variables for OS and Project
os_type = os.environ.get("OS")
project = os.environ.get("PROJECT")

if not os_type:
    raise ValueError("OS environment variable must be set")

if os_type not in [os_type.value for os_type in OSType]:
    raise ValueError(
        f"Invalid OS: {os_type}. Must be one of: "
        f"{[os_type.value for os_type in OSType]}"
    )

if not project:
    raise ValueError("PROJECT environment variable must be set")

if project not in [project.value for project in ProjectType]:
    raise ValueError(
        f"Invalid PROJECT: {project}. Must be one of: "
        f"{[project.value for project in ProjectType]}"
    )

state.os = os_type
state.project = project

def api_response_callback(request, response, error):
    """Handle API responses"""
    response_id = datetime.now().isoformat()
    state.responses[response_id] = (request, response)
    if error:
        print(f"\n\nAI Model - API Error: ")
        print(f"{error}")
        print(f"request: {request}")
        print(f"response: {response}")
        
def tool_output_callback(tool_output, tool_id):
    """Handle tool outputs"""
    state.tools[tool_id] = tool_output
    # Add the tool result to the messages for the user to see
    if state.messages and state.messages[-1].role == "assistant":
        if isinstance(state.messages[-1].content, list):
            state.messages[-1].content.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": tool_output.output if hasattr(tool_output, "output") else "",
                "is_error": hasattr(tool_output, "error") and bool(tool_output.error)
            })

@app.get("/health")
def get_health(request: Request):
    return {"message": "success"}


@app.get("/", response_class=HTMLResponse)
def get_home(request: Request):
    """Render the main page"""
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "state": state.dict(),
            "warning": "⚠️ Security disclaimer: We never store or train on your data."
        }
    )

@contextmanager
def track_sampling_loop():
    state.in_sampling_loop = True
    yield
    state.in_sampling_loop = False

@app.post("/send_message")
async def send_message(message_req: MessageRequest):
    """Process a message from the user"""
    global state
    
    # Add debugging
    print(f"Before processing - Message count: {len(state.messages)}")
    
    # Add the user message to the state
    state.messages = message_req.messages
    # state.messages.append(Message(role="user", content=message_req.messages[0].content))
    print(f"After adding user message - Message count: {len(state.messages)}")
    
    # Create a copy of the messages to maintain original state
    original_messages = state.messages.copy()
    response_messages = []
    # Process the message
    try:
        with track_sampling_loop():
            result_messages = await sampling_loop(
                os=OSType(state.os),
                project=ProjectType(state.project),
                ip_address=state.ip_address,
                system_prompt_suffix=state.custom_system_prompt,
                model=state.model,
                provider=state.provider,
                messages=[m.to_dict() for m in state.messages],  # Convert Pydantic models to dicts
                output_callback=lambda msg: state.messages.append(
                    Message(role="assistant", isNew=True, content=[msg] if isinstance(msg, dict) else msg)
                ),
                tool_output_callback=tool_output_callback,
                api_response_callback=api_response_callback,
                api_key=state.api_keys[state.provider],
                only_n_most_recent_images=state.only_n_most_recent_images,
            )
            
            # Don't overwrite the state.messages with returned value from sampling_loop
            # The output_callback should have already updated state.messages
            # If result_messages is not None and we want to use it instead, convert it to Message objects first
            if result_messages and len(result_messages) > len(state.messages):
                print(f"Using result_messages from sampling_loop: {len(result_messages)} messages")
                # Convert dict messages to Message objects if needed
                state.messages = [m if isinstance(m, Message) else Message(**m) for m in result_messages]
            
            # Safety check - if messages were lost, restore from original + any new ones
            if len(state.messages) <= len(original_messages):
                print("Warning: Messages may have been lost during processing. Restoring from original.")
                # Find the last assistant message that might have been added via callback
                assistant_messages = [msg for msg in state.messages if msg.role == "assistant" 
                                     and msg not in original_messages]
                if assistant_messages:
                    state.messages = original_messages + assistant_messages
    except Exception as e:
        error_message = str(e)
        traceback_str = traceback.format_exc()
        print(f"Error in send_message: {error_message}")
        print(traceback_str)
        return JSONResponse(
            status_code=500,
            content={"error": error_message, "traceback": traceback_str}
        )
    
    # Convert the messages for the response
    messages_for_response = []
    for msg in state.messages:
        try:
            if isinstance(msg.content, str):
                messages_for_response.append({"role": msg.role, "isNew": msg.isNew, "content": msg.content, "extra": msg})
            elif isinstance(msg.content, list):
                # Process complex content (images, tool results, etc.)
                content_for_response = []
                for block in msg.content:
                    if isinstance(block, dict):
                        if block.get("type") == "tool_result" and block.get("tool_use_id") in state.tools:
                            tool_result = state.tools[block.get("tool_use_id")]
                            content_block = {
                                "type": "tool_result",
                                "content": tool_result,
                                "originalBlock": block
                            }
                            # ignoring is other unknown tool types, 
                            # only showing image type tool results if hide_images is not set
                            # if tool_result.type == 'image' and not state.hide_images:
                            messages_for_response.append({
                                "role": msg.role, "isNew":msg.isNew, "content": "tool", "extra": content_block
                            })

                        else:
                            content_for_response.append(block)
                    elif block.type == "text":
                        messages_for_response.append({"role": msg.role, "isNew":msg.isNew, "content": block.text, "extra": block})
                    else:
                        print(f"state.tools[block[\"id\"]]: {state.tools[block.id]['type']}")
                print(f"content_for_response: {content_for_response}, msg.role: {msg.role}, msg.content: {msg.content}")
                # messages_for_response.append({"role": msg.role, "content": content_for_response})
        except Exception as e:
            print(f"Error processing message: {e}")
    
    print(f"Messages for response: {len(messages_for_response)}")

    return {"messages": messages_for_response}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
