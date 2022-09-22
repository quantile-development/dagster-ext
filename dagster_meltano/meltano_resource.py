import json
import subprocess
from typing import List, Optional

from dagster import job, op

from dagster_meltano.utils import Singleton, generate_dagster_name


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

    @property
    def jobs(self) -> List[dict]:
        meltano_jobs = self.run_cli(["job", "list", "--format=json"])

        for meltano_job in meltano_jobs["jobs"]:

            @op(name=f'run_{generate_dagster_name(meltano_job["job_name"])}')
            def dagster_op():
                print(
                    subprocess.run(
                        [self.meltano_bin, "--help"],
                        cwd=self.project_dir,
                        stdout=subprocess.PIPE,
                        universal_newlines=True,
                        check=True,
                    ).stdout
                )

            @job(name=generate_dagster_name(meltano_job["job_name"]))
            def dagster_job():
                dagster_op()

            yield dagster_job

    @property
    def schedules(self) -> List[dict]:
        return self.run_cli(["schedule", "list", "--format=json"])
