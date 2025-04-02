# Deployment Guide

## Cloud Deployment Options

The system can be deployed in different configurations, including a split setup where the environment runs in the cloud while the agent runs locally. This is particularly useful for:
- Running resource-intensive environments
- Accessing cloud-specific resources
- Maintaining separation between agent and environment

### Remote Environment Setup (Cloud Provider)

You can deploy the environment component to various cloud providers. Here's how to set it up on AWS EC2 (similar steps apply to other providers):

1. Launch an instance with Docker support
2. Configure security groups to allow:
   - Port 50051 (gRPC communication)
   - Port 6080 (VNC web access)
   - Port 5900 (Direct VNC access)

3. On the cloud instance, run the environment:

```bash
# Build the server image
docker build . -t enterprise-computer-use-server:local -f Dockerfile.server

# Run the container
export OS=linux
export PROJECT=%your_project_name%  # e.g., claude_computer_use
docker run \
    -e OS=$OS \
    -e PROJECT=$PROJECT \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/enterprise_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 6080:6080 \
    -p 50051:50051 \
    -it enterprise-computer-use-server:local
```

### Local Agent Setup

With the remote environment running, set up the local agent:

```bash
# Build the client image
docker build . -t enterprise-computer-use-client:local -f Dockerfile.client

# Run the container
export ANTHROPIC_API_KEY=%your_api_key%
export IP_ADDRESS=%your_cloud_instance_ip%
export OS=linux
export PROJECT=%your_project_name%
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -e OS=$OS \
    -e PROJECT=$PROJECT \
    -e IP_ADDRESS=$IP_ADDRESS \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/enterprise_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 8501:8501 \
    -p 8080:8080 \
    -it enterprise-computer-use-client:local
```

### Architecture Overview

```
┌─────────────┐         ┌──────────────────┐
│ Local Agent │ ◄─────► │ Remote Environment│
│ (Your PC)   │   gRPC  │  (Cloud Instance)│
└─────────────┘         └──────────────────┘
     │                          │
     │ API Calls               │ Virtual Desktop
     ▼                          ▼
┌─────────────┐         ┌──────────────────┐
│   AI Model  │         │  VNC Access      │
└─────────────┘         └──────────────────┘
```
