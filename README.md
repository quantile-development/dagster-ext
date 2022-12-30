# Meltano Dagster Extention

[![PyPI version](https://badge.fury.io/py/dagster-ext.svg)](https://badge.fury.io/py/dagster-ext)

This project uses [`dagster-meltano`](https://github.com/quantile-development/dagster-meltano) under the hood.

## Features

- Load all Meltano jobs as Dagster jobs.
- Add all correspondig schedules to these jobs.
- (todo) Load all DBT models as Dagster assets.
- (todo) Load all Singer tap streams as Dagster assets.
- (todo) Ops to perform all Meltano actions.
- (todo) Extract Singer metrics from logs and store them using Dagster.

## Installation

```sh
# Add the dagster-ext to your Meltano project
meltano add utility dagster

# Initialize your Dagster project
meltano invoke dagster:initialize

# Start Dagit
meltano invoke dagster:start
```

## Commands

```sh
meltano invoke dagster:initialize
```

Setup a new Dagster project and automatically load jobs and assets from your Meltano project.

```sh
meltano invoke dagster:start
```

Start Dagit to serve your local Dagster deployment.
