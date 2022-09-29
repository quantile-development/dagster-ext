# Meltano Dagster Extention

[![PyPI version](https://badge.fury.io/py/dagster-ext.svg)](https://badge.fury.io/py/dagster-ext)

Description here

## Installation

```sh
# Add the dagster-ext to your Meltano project
meltano add utility dagster-ext

# Initialize your Dagster project
meltano invoke dagster:initialize

# Start Dagit
meltano invoke dagster:up
```

## Commands

```sh
meltano invoke dagster:initialize (dagster:init)
```

Setup a new Dagster project and automatically load jobs and assets from your Meltano project.

```sh
meltano invoke dagster:up
```

Start Dagit to serve your local Dagster deployment.
