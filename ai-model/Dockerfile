FROM fattanishakir/claude-computer-use-ai-model-baseline:latest

ARG DISPLAY_NUM=1
ARG HEIGHT=768
ARG WIDTH=1024

ENV USERNAME=computeruse
ENV HOME=/home/$USERNAME
WORKDIR /home/computeruse

USER root
# only reinstall if requirements.txt changes
COPY enterprise_computer_use/requirements.txt /home/computeruse/enterprise_computer_use/requirements.txt
RUN python -m pip install -r /home/computeruse/enterprise_computer_use/requirements.txt

# setup desktop env & app
COPY image/ /home/computeruse
COPY enterprise_computer_use/ /home/computeruse/enterprise_computer_use/

RUN chown -R $USERNAME:$USERNAME /home/computeruse

USER computeruse
ENV DISPLAY_NUM=$DISPLAY_NUM
ENV HEIGHT=$HEIGHT
ENV WIDTH=$WIDTH
ENV IP_ADDRESS=localhost
ENV OS=linux
ENV PROJECT=claude_computer_use

ENTRYPOINT [ "./entrypoint.sh" ]
