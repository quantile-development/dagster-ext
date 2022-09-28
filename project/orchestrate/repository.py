import os
from pathlib import Path

from dagster import repository, with_resources
from dagster_dbt import dbt_cli_resource
from dagster_meltano import (
    load_assets_from_meltano_project,
    load_jobs_from_meltano_project,
    meltano_resource,
)

MELTANO_PROJECT_DIR = os.getenv("MELTANO_PROJECT_ROOT", os.getcwd())
MELTANO_BIN = os.getenv("MELTANO_BIN", "meltano")

DBT_PROJECT_DIR = Path(MELTANO_PROJECT_DIR) / "transform"
DBT_PROFILES_DIR = Path(MELTANO_PROJECT_DIR) / "transform" / "profiles" / "postgres"
DBT_TARGET_DIR = Path(MELTANO_PROJECT_DIR) / ".meltano" / "transformers" / "dbt" / "target"

meltano_jobs = load_jobs_from_meltano_project(MELTANO_PROJECT_DIR)


@repository
def repository():
    return [
        meltano_jobs,
        with_resources(
            load_assets_from_meltano_project(
                meltano_project_dir=MELTANO_PROJECT_DIR,
                dbt_project_dir=str(DBT_PROJECT_DIR),
                dbt_profiles_dir=str(DBT_PROFILES_DIR),
                dbt_target_dir=str(DBT_TARGET_DIR),
                dbt_use_build_command=True,
            ),
            {
                "meltano": meltano_resource,
                "dbt": dbt_cli_resource.configured(
                    {
                        "project_dir": str(DBT_PROJECT_DIR),
                        "profiles_dir": str(DBT_PROFILES_DIR),
                        "target_path": str(DBT_TARGET_DIR),
                        # "dbt_executable": "/dagster-testing/.meltano/transformers/dbt-postgres/venv/bin/dbt",
                    },
                ),
            },
        ),
    ]
