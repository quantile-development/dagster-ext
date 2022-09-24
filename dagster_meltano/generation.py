import json
import logging
import subprocess
from typing import List, Optional, Union

from dagster import JobDefinition, ScheduleDefinition

from dagster_meltano.meltano_resource import MeltanoResource


def load_jobs_from_meltano_project(
    project_dir: Optional[str],
) -> List[Union[JobDefinition, ScheduleDefinition]]:
    """This function generates dagster jobs for all jobs defined in the Meltano project. If there are schedules connected
    to the jobs, it also returns those.

    Args:
        project_dir (Optional[str], optional): The location of the Meltano project. Defaults to os.getenv("MELTANO_PROJECT_ROOT").

    Returns:
        List[Union[JobDefinition, ScheduleDefinition]]: Returns a list of either Dagster JobDefinitions or ScheduleDefinitions
    """
    meltano_resource = MeltanoResource(project_dir)
    meltano_jobs = meltano_resource.jobs

    return list(meltano_jobs)


if __name__ == "__main__":
    load_jobs_from_meltano_project("/workspace/meltano")
