# Use python image as a base
FROM python:3.8

# Set the workdir to the final Dagster workdir
WORKDIR /opt/dagster/app

# Set the meltano project root to the Dagster root
ENV MELTANO_PROJECT_ROOT /opt/dagster/app

# Install pipx
RUN pip install pipx

# Make sure the pipx install location is in the path
ENV PATH "$PATH:/root/.local/bin"

# Install meltano
RUN pipx install meltano

# Make sure we install the requirements
RUN pip install dagster-ext dagster-cloud

# Copy the meltano project root to the working dir
COPY . /opt/dagster/app

# Remove the .meltano folder
RUN rm -rf .meltano

# Install all Meltano plugins
RUN meltano install