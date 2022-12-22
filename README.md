# Meltano Dagster Extention

[![PyPI version](https://badge.fury.io/py/dagster-ext.svg)](https://badge.fury.io/py/dagster-ext)

This project is still a work in progress. Please create an issue if you find any bugs.

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

## Code Examples

Below are some code examples how to use the `dagster-meltano` package.

### Automatically load all jobs and schedules from your Meltano project.

```python
from dagster import repository

from dagster_meltano import load_jobs_from_meltano_project

meltano_jobs = load_jobs_from_meltano_project("<path-to-meltano-root>")

@repository
def repository():
    return [meltano_jobs]
```

### Install all Meltano plugins

```python
from dagster import repository, job

from dagster_meltano import meltano_resource, meltano_install_op

@job(resource_defs={"meltano": meltano_resource})
def install_job():
    meltano_install_op()

@repository()
def repository():
    return [install_job]
```

### Create an arbitrary Meltano run command

```python
from dagster import repository, job

from dagster_meltano import meltano_resource, meltano_run_op

@job(resource_defs={"meltano": meltano_resource})
def meltano_run_job():
    tap_done = meltano_run_op("tap-1 target-1")()
    meltano_run_op("tap-2 target-2")(tap_done)

@repository()
def repository():
    return [meltano_run_job]
```
