docker build . -t planner-grounding-computer-use:local  # manually build the docker image (optional)
export ANTHROPIC_API_KEY=your_claude_api_key
export OS=linux
export PROJECT=planner_grounding_computer_use
export GROUNDING_MODEL_URL=your_grounding_model_url

docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -e GROUNDING_MODEL_URL=$GROUNDING_MODEL_URL \
    -e OS=$OS \
    -e PROJECT=$PROJECT \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/planner_grounding_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it planner-grounding-computer-use:local
