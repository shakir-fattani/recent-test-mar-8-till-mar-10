# Development Configuration Options

## Model Selection and API Providers

You can configure different AI models and API providers by setting the appropriate environment variables:

### Direct API Access
```bash
# For Claude (default)
export ANTHROPIC_API_KEY=%your_api_key%

# For OpenAI
export OPENAI_API_KEY=%your_api_key%

# For Gemini (planned)
export GOOGLE_API_KEY=%your_api_key%
```

### AWS Bedrock
```bash
# Option 1: Using AWS Profile
export API_PROVIDER=bedrock
export AWS_PROFILE=%your_aws_profile%
export AWS_REGION=%your_aws_region%

# Option 2: Using Access Keys
export API_PROVIDER=bedrock
export AWS_ACCESS_KEY_ID=%your_aws_access_key%
export AWS_SECRET_ACCESS_KEY=%your_aws_secret_access_key%
export AWS_SESSION_TOKEN=%your_aws_session_token%  # if using temporary credentials
export AWS_REGION=%your_aws_region%
```

### Google Vertex AI
```bash
export API_PROVIDER=vertex
export CLOUD_ML_REGION=%your_vertex_region%
export ANTHROPIC_VERTEX_PROJECT_ID=%your_vertex_project_id%
# Ensure you have authenticated using: gcloud auth application-default login
```

## Operating System Configuration
Set the `OS` environment variable to specify the target environment:
```bash
export OS=linux    # For Linux virtual environment
export OS=mac      # For macOS host machine control
```

## Project Selection
The `PROJECT` variable determines which implementation to use:
```bash
export PROJECT=claude_computer_use     # Claude implementation
export PROJECT=openai_computer_use     # OpenAI implementation
export PROJECT=gemini_computer_use     # Gemini implementation (planned)
```

## Docker Environment (Linux Virtual Environment)

The Docker configuration varies based on your chosen API provider:

### For Direct Anthropic API:
```bash
docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it enterprise-computer-use:local
```

### For AWS Bedrock:
```bash
# Using AWS Profile
docker run \
    -e API_PROVIDER=bedrock \
    -e AWS_PROFILE=$AWS_PROFILE \
    -e AWS_REGION=$AWS_REGION \
    -v $HOME/.aws:/home/computeruse/.aws \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it enterprise-computer-use:local
```

### For Google Vertex AI:
```bash
docker run \
    -e API_PROVIDER=vertex \
    -e CLOUD_ML_REGION=$VERTEX_REGION \
    -e ANTHROPIC_VERTEX_PROJECT_ID=$VERTEX_PROJECT_ID \
    -v $HOME/.config/gcloud/application_default_credentials.json:/home/computeruse/.config/gcloud/application_default_credentials.json \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it enterprise-computer-use:local
```

## gRPC Network: Generate Protobuf Files

The protobuf files are generated automatically using GRPC tools:

```bash
cd protobuf-definitions
bash make.sh
```
