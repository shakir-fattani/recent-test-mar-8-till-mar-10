docker build . -t airtable-computer-use:local  # manually build the docker image (optional)


docker run \
    -e ANTHROPIC_API_KEY=$ANTHROPIC_API_KEY \
    -e AIRTABLE_API_KEY=$AIRTABLE_API_KEY \
    -e OS=$OS \
    -e PROJECT=$PROJECT \
    -v $(pwd)/enterprise_computer_use:/home/computeruse/airtable_computer_use/ \
    -v $HOME/.anthropic:/home/computeruse/.anthropic \
    -v $(pwd)/credentials.json:/home/computeruse/credentials.json \
    -v $(pwd)/token.json:/home/computeruse/token.json \
    -p 5900:5900 \
    -p 8501:8501 \
    -p 6080:6080 \
    -p 8080:8080 \
    -p 50051:50051 \
    -it airtable-computer-use:local
