FROM python:3.8

RUN pip install pipx

ENV PATH "$PATH:/root/.local/bin"

RUN pipx install meltano==2.6.0

COPY orchestrate/dagster/dagster_cloud_post_install.sh /opt/dagster/app/dagster_cloud_post_install.sh