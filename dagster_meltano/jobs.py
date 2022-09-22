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

    list_result = subprocess.run(
        [meltano_resource.meltano_bin, "schedule", "list", "--format=json"],
        cwd=meltano_resource.project_dir,
        stdout=subprocess.PIPE,
        universal_newlines=True,
        check=True,
    )

    schedule_export = json.loads(list_result.stdout)
    logging.info(schedule_export)

    return []
