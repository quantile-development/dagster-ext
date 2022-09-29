# Meltano Dagster Extention

[![PyPI version](https://badge.fury.io/py/dagster-ext.svg)](https://badge.fury.io/py/dagster-ext)

This project is still a work in progress. Please create an issue if you find any bugs. 

## Features
- Load all Meltano jobs as Dagster jobs.
- Add all correspondig schedules to these jobs.
- Load all DBT models as Dagster assets.
- (todo) Load all Singer tap streams as Dagster assets.
- (todo) Ops to perform all Meltano actions.
- (todo) Extract Singer metrics from logs and store them using Dagster.

## Installation
(You cannot use the `meltano add` yet.)

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
