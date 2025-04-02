# Concur Computer Use Project

This document describes the Concur Computer Use project implementation, which enables Claude to automate expense report creation in Concur by processing receipts using either Cambio's AnyParser or Claude's multimodal capabilities.

## Overview

The Concur Computer Use project extends the base Computer Use functionality with receipt parsing capabilities, allowing Claude to:
- Parse receipt images using Claude's vision or Cambio's AnyParser
- Extract key receipt information (date, amount, vendor, etc.)
- Navigate and fill Concur expense reports

## Prerequisites

1. **API Keys**:
   - Anthropic API key for Claude
   - Cambio API key from [Cambio Account Page](https://www.cambioml.com/account)

2. **Environment Setup**:
   ```bash
   export ANTHROPIC_API_KEY=your_api_key_here
   export CAMBIO_API_KEY=your_cambio_api_key_here
   export OS=linux
   export PROJECT=concur_computer_use
   ```

## Components

### Tools
- `ComputerTool`: Handles GUI interactions with Concur interface
- `BashTool`: Executes system commands
- `EditTool`: Manages file operations
- `AnyParserTool`: Processes receipt images using Cambio's API

### Receipt Processing Options

1. **Cambio AnyParser**:
   - Specialized receipt parsing with high accuracy
   - Structured output format
   - Supports multiple languages and receipt formats
   - Usage example:
     ```python
     await anyparser_tool(
         command="parse",
         filepath="/path/to/receipt.jpg"
     )
     ```

2. **Claude Multimodal**:
   - Direct image analysis using Claude's vision capabilities
   - More flexible for unusual receipt formats
   - Natural language understanding of receipt contents
   - Handles complex layouts and annotations

## Usage

```bash
./scripts/launch_linux_concur_computer_use.sh
```
