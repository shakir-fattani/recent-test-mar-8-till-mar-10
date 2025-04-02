docker run -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY -e OS=$OS -e PROJECT=$PROJECT \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/enterprise_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -p 5900:5900 -p 8000:8000 -p 8501:8501 -p 6080:6080 -p 8080:8080 -p 50051:50051 -it enterprise-computer-use:local
