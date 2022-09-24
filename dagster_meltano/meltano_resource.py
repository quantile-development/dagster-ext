import json
import logging
import subprocess
from typing import List, Optional

import dagster
from dagster import In, Nothing, get_dagster_logger, job, op

from dagster_meltano.utils import Singleton, generate_dagster_name

logger = get_dagster_logger()


class MeltanoResource(metaclass=Singleton):
    def __init__(self, project_dir: str, meltano_bin: Optional[str] = "meltano"):
        self.project_dir = project_dir
        self.meltano_bin = meltano_bin

    # TODO: Refactor to different file
    def run_cli(self, commands: List[str]):
        return json.loads(
            subprocess.run(
                [self.meltano_bin] + commands,
                cwd=self.project_dir,
                stdout=subprocess.PIPE,
                universal_newlines=True,
                check=True,
            ).stdout
        )

    def create_meltano_task_op(self, task: str):
        @op(name=generate_dagster_name(task), ins={"after": In(dagster.Nothing)})
        def dagster_op():
            logger.info(self.run_cli(["run", task]))

        return dagster_op

    @property
    def jobs(self) -> List[dict]:
        meltano_jobs = self.run_cli(["job", "list", "--format=json"])

        for meltano_job in meltano_jobs["jobs"]:
            logging.warning(meltano_job)

            @job(name=generate_dagster_name(meltano_job["job_name"]))
            def dagster_job():
                meltano_task_done = None
                for task in meltano_job["tasks"]:
                    meltano_task_op = self.create_meltano_task_op(task)
                    if meltano_task_done:
                        meltano_task_done = meltano_task_op(meltano_task_done)
                    else:
                        meltano_task_done = meltano_task_op()

            yield dagster_job

    @property
    def schedules(self) -> List[dict]:
        return self.run_cli(["schedule", "list", "--format=json"])
