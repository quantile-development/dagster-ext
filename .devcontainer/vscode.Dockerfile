FROM quantiledevelopment/vscode-python:3.8

RUN pipx install meltano==2.6.0

RUN pipx upgrade poetry