import os
from pathlib import Path

from dagster import repository, with_resources

from dagster_meltano import (
    load_assets_from_meltano_project,
    load_jobs_from_meltano_project,
    meltano_resource,
)

MELTANO_PROJECT_DIR = os.getenv("MELTANO_PROJECT_ROOT", os.getcwd())
MELTANO_BIN = os.getenv("MELTANO_BIN", "meltano")

meltano_jobs = load_jobs_from_meltano_project(MELTANO_PROJECT_DIR)


@repository
def meltano():
    return [
        meltano_jobs, 
        with_resources(
            load_assets_from_meltano_project(
                meltano_project_dir=MELTANO_PROJECT_DIR,
            ),
            {
                "meltano": meltano_resource,
            },
        )
    ]
