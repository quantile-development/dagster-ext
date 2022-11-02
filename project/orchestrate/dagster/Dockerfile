FROM python:3.8

RUN pip install pipx

RUN pipx ensurepath

ENV PATH "$PATH:/root/.local/bin"

RUN pipx install meltano==2.6.0

ENTRYPOINT []