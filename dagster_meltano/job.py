from dagster import In, JobDefinition, Nothing, OpDefinition, job, op

from dagster_meltano.meltano_invoker import MeltanoInvoker
from dagster_meltano.utils import generate_dagster_name, run_cli


class Job:
    def __init__(self, meltano_job: dict, meltano_invoker: MeltanoInvoker) -> None:
        self.name = meltano_job["job_name"]
        self.tasks = meltano_job["tasks"]
        self.meltano_invoker = meltano_invoker

    @property
    def dagster_name(self) -> str:
        return generate_dagster_name(self.name)

    def task_op_factory(self, task: str):
        @op(
            name=generate_dagster_name(task),
            description=f"Run `{task}` using Meltano.",
            ins={"after": In(Nothing)},
            tags={"kind": "meltano"},
        )
        def dagster_op():
            self.meltano_invoker.run_and_log(f"run {task}")

        return dagster_op

    @property
    def dagster_job(self) -> JobDefinition:
        @job(
            name=self.dagster_name,
        )
        def dagster_meltano_job():
            meltano_task_done = None
            for task in self.tasks:
                meltano_task_op = self.task_op_factory(task)
                if meltano_task_done:
                    meltano_task_done = meltano_task_op(meltano_task_done)
                else:
                    meltano_task_done = meltano_task_op()

        return dagster_meltano_job
