# Enterprise Computer Use

This project provides a flexible framework for AI-powered computer interaction, supporting multiple models, tools, and deployment configurations. At its core, it enables AI agents to perform tasks through both virtual and native desktop environments while maintaining strict security controls and monitoring capabilities. The system provides 3 options for deployment:
1. run locally via Docker container, or
2. run locally via the host machine, or
3. run remotely through gRPC communication, allowing for distributed deployment scenarios.

## Project Structure

```bash
📦 enterprise_computer_use
 ┣ 🤖 agent
 ┃ ┣ 📄 claude_agent.py     # Claude 3.5 integration
 ┃ ┣ 📄 openai_agent.py     # OpenAI integration (experimental)
 ┃ ┣ 📄 gemini_agent.py     # Gemini integration (planned)
 ┃ ┗ 📄 ...
 ┣ 🔌 communication
 ┃ ┣ 📄 computer_use_client.py
 ┃ ┣ 📄 computer_use_server.py
 ┃ ┗ 📄 ...
 ┣ 🌍 env
 ┃ ┣ 📄 computer_use_env.py
 ┃ ┗ 📄 ...
 ┣ 📦 objects
 ┃ ┣ 📄 computer_use_pb2.py
 ┃ ┗ 📄 ...
 ┣ 🖥️ project
 ┃ ┣ 📄 linux_claude_computer_use.py
 ┃ ┣ 📄 mac_claude_computer_use.py
 ┃ ┗ 📄 ...
 ┣ 🛠️ tools
 ┃ ┣ 📄 base.py             # Base tool interface
 ┃ ┣ 📂 claude/             # Claude-specific tools
 ┃ ┣ 📂 third_party/        # External service integrations
 ┃ ┗ 📄 ...
 ┗ 🌐 streamlit.py          # Web interface
```

## Quickstart

You can run the project in 3 different ways:
1. run locally via Docker container, or
2. run locally via the host machine, or
3. run remotely through gRPC communication, allowing for distributed deployment scenarios.

We will go through each of these options in the following sections.

### 1. Run local control Linux virtual environment in docker

1. Setup prerequisites:

- [Docker](https://www.docker.com/) installed and running on your system
- An Anthropic API key (sign up at https://www.anthropic.com)

2. Build the docker image:

> [!NOTE]
> It will take a while to build the docker image.

```bash
docker build . -t enterprise-computer-use:local  # manually build the docker image
```

3. Run the docker container:

> [!NOTE]
> Update the `ANTHROPIC_API_KEY` environment variable with your own API key.

```bash
export ANTHROPIC_API_KEY=%your_api_key%
export OS=linux
export PROJECT=claude_computer_use # project name, for example claude_computer_use
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -e OS=$OS \
    -e PROJECT=$PROJECT \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/enterprise_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8000:8000 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it enterprise-computer-use:local
```

#### Accessing the demo app

Once the container is running, open your browser to [http://localhost:8080](http://localhost:8080) to access the combined interface that includes both the agent chat and desktop view.

The container stores settings like the API key and custom system prompt in `~/.anthropic/`. Mount this directory to persist these settings between container runs.

Alternative access points:

- Streamlit interface only: [http://localhost:8501](http://localhost:8501)
- Desktop view only: [http://localhost:6080/vnc.html](http://localhost:6080/vnc.html)
- Direct VNC connection: `vnc://localhost:5900` (for VNC clients)

#### Screen size

Environment variables `WIDTH` and `HEIGHT` can be used to set the screen size. For example:

```bash
    -e WIDTH=1920 \
    -e HEIGHT=1080 \
```

We do not recommend sending screenshots in resolutions above [XGA/WXGA](https://en.wikipedia.org/wiki/Display_resolution_standards#XGA) to avoid issues related to [image resizing](https://docs.anthropic.com/en/docs/build-with-claude/vision#evaluate-image-size).
Relying on the image resizing behavior in the API will result in lower model accuracy and slower performance than implementing scaling in your tools directly. The `computer` tool implementation in this project demonstrates how to scale both images and coordinates from higher resolutions to the suggested resolutions.

When implementing computer use yourself, we recommend using XGA resolution
(1024x768):

- For higher resolutions: Scale the image down to XGA and let the model interact with this scaled version, then map the coordinates back to the original resolution proportionally.
- For lower resolutions or smaller devices (e.g. mobile devices): Add black padding around the display area until it reaches 1024x768.

The docker run command above mounts the repo inside the docker image, such that you can edit files from the host. Streamlit is already configured with auto reloading.

### 2. Run local control host machine (macOS Only)

> [!IMPORTANT]
> The local machine control feature currently supports **macOS only**. Windows and Linux support is not available at this time.

To run the Streamlit app locally and control your Mac:

1. Install dependencies:

```bash
./setup.sh  # Sets up virtual environment and installs required packages
```

2. Configure your API key and run the app:

> [!NOTE]
> Update the `ANTHROPIC_API_KEY` environment variable with your own API key.

```bash
export ANTHROPIC_API_KEY=your_api_key_here
export OS=mac
export PROJECT=claude_computer_use # project name, for example claude_computer_use
```

Then run the app:

```bash
STREAMLIT_SERVER_PORT=8501 python -m streamlit run enterprise_computer_use/streamlit.py
```

The app will be available at http://localhost:8501 in your browser and you need to select `mac` as the machine.

`NOTE`: caveat is that when build a docker there is complexity in getting the docker to use pyautogui display to work on host machine.

### (WIP) 3. Run remotely through gRPC communication




## Use Cases (aka Projects)

The framework includes several project implementations that demonstrate different use cases and configurations:

### Claude Computer Use

The primary project implementation showcasing AI-powered computer interaction:

- **Linux Virtual Environment**:
  - Runs in Docker container
  - Full GUI interaction capabilities
  - Firefox-ESR browser control
  - System command execution

- **macOS Local Control**:
  - Direct host machine interaction
  - Native application control (Chrome, Outlook, Slack)
  - GUI automation via PyAutoGUI
  - System command integration

For detailed implementation information, see the [Claude Computer Use Guide](docs/project/claude_computer_use.md).

### Adding New Projects

To add your own project implementation, please follow our [Project Development Guide](docs/project/project.md) which covers:

- Project structure and requirements
- System prompt configuration
- Tool collection setup
- Best practices and examples

The Claude Computer Use implementation serves as a reference example for creating new projects. More example projects will be added in future releases.

For detailed information about:

- Project development guidelines
- System prompt design
- Tool configuration
- Error handling

See our [Project Development Guide](docs/project/project.md).

## Advanced Topics

For detailed information about:

- Using different AI models (Claude, OpenAI, Gemini)
- Operating system configurations
- Project implementations
- Docker environment setup
- gRPC network configuration

See our [Development Guide](docs/development.md).

For information about cloud deployment options and remote environments:

- Remote environment configuration
- Architecture overview

See our [Deployment Guide](docs/deployment.md).
