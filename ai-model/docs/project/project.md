# Project Development Guide

This guide provides instructions and best practices for creating new projects in the enterprise computer use framework.

## Overview

Projects in this framework define how AI agents interact with specific
environments and tools. Each project includes configuration for:

- System prompts
- Tool collections
- Client communication
- Environment settings

## Creating New Projects

To create a new project similar to Claude Computer Use:

1. Create a new file in `enterprise_computer_use/project/`
2. Define your system prompt with:
   - Environment capabilities
   - Tool usage guidelines
   - Important warnings/restrictions
3. Register your project using the `@Registry.register` decorator
4. Configure your tool collection and client factory

See the [Claude Computer Use](claude_computer_use.md) implementation for reference.

## Best Practices

### System Prompts

- Clearly define environment capabilities
- Include specific tool usage instructions
- Document important restrictions
- Add relevant warnings

### Tool Configuration

- Use appropriate tools for the environment
- Configure screen resolution and scaling
- Handle environment-specific requirements

### Error Handling

- Validate environment requirements
- Handle tool initialization failures
- Provide clear error messages

### Documentation

- Document all environment requirements
- Provide clear setup instructions
- Include usage examples
- List known limitations

## Project Examples

- [Claude Computer Use](claude_computer_use.md): Demonstrates both Linux VM and macOS implementations
- More examples coming soon...
