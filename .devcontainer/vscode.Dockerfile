FROM quantiledevelopment/vscode-python:3.9

ENV MELTANO_PROJECT_ROOT=/workspace/meltano

RUN pipx install meltano==2.6.0