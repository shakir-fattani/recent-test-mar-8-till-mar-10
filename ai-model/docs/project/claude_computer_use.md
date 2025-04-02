# Claude Computer Use Project

This document describes the Claude Computer Use project implementation, which enables Claude to interact with both Linux virtual machines and local macOS environments.

## Overview

The Claude Computer Use project provides two main implementations:
- Linux-based virtual machine control (via Docker)
- Local macOS control

Both implementations use Claude's computer-use capability to interact with graphical interfaces and execute system commands.

## Components

### Tools
- `ComputerTool`/`GUIComputerTool`: Handles mouse movements, clicks, and screenshots
- `BashTool`: Executes system commands
- `EditTool`: Manages file operations and text editing

### System Prompts

Both implementations include carefully crafted system prompts that provide Claude with:
- Environment context and capabilities
- Application interaction guidelines
- Best practices for tool usage
- Important warnings and restrictions

## Linux Implementation

The Linux implementation ([linux_claude_computer_use.py](../enterprise_computer_use/project/linux_claude_computer_use.py)) is designed for Docker environments and includes:

1. **Environment**:
   - Ubuntu virtual machine
   - Firefox-ESR browser
   - X11 display server
   - Full internet access

2. **Key Features**:
   - GUI application launching with DISPLAY=:1
   - Firefox browser control
   - File system access
   - Screenshot capabilities

3. **Configuration**:
   - Uses `ComputerTool` for GUI interactions
   - Integrates `BashTool` for system commands
   - Implements `EditTool` for file operations
   - Configures `ComputerUseClient` for communication

## macOS Implementation

The macOS implementation ([mac_claude_computer_use.py](../enterprise_computer_use/project/mac_claude_computer_use.py)) provides direct control of the local machine:

1. **Environment**:
   - Native macOS system
   - Local application control
   - PyAutoGUI integration

2. **Key Features**:
   - Native application launching (Chrome, Outlook, Slack)
   - GUI element interaction
   - Screenshot verification
   - Clipboard operations

3. **Configuration**:
   - Uses `GUIComputerTool` for native macOS interactions
   - Integrates `BashTool` for system commands
   - Implements `EditTool` for file operations
   - Configures `LocalComputerUseClient` for direct control
