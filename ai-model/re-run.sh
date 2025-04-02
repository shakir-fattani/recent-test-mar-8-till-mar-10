docker stop $(docker ps -aq) && docker rm $(docker ps -aq) && docker image rm enterprise-computer-use:local  && bash ./build.sh && bash ./run.sh
