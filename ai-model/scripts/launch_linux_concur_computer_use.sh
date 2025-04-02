./setup.sh  # configure venv, install development dependencies, and install pre-commit hooks
docker build . -t concur-computer-use:local  # manually build the docker image (optional)
export OS=linux
export PROJECT=concur_computer_use
export ANTHROPIC_API_KEY=your_anthropic_api_key
export CAMBIO_API_KEY=your_cambio_api_key

docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -e CAMBIO_API_KEY=$CAMBIO_API_KEY \
    -e OS=$OS \
    -e PROJECT=$PROJECT \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/concur_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it concur-computer-use:local
