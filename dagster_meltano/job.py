from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import TYPE_CHECKING

from dagster import (
    In,
    JobDefinition,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    get_dagster_logger,
    job,
    op,
)

from dagster_meltano.meltano_invoker import MeltanoInvoker
from dagster_meltano.utils import generate_dagster_name

if TYPE_CHECKING:
    from dagster_meltano.meltano_resource import MeltanoResource

dagster_logger = get_dagster_logger()


async def log_processor(reader: asyncio.streams.StreamReader, log_type: str) -> None:
    """Log the output of a stream.

    Args:
        reader: The stream reader to read from.
    """
    # TODO: Clean up the logging
    while True:
        if reader.at_eof():
            break
        data = await reader.readline()
        log_line_raw = data.decode("utf-8").rstrip()

        if not log_line_raw:
            continue

        try:
            log_line = json.loads(log_line_raw)

            if log_line.get("level") == "debug":
                dagster_logger.debug(log_line.get("event", log_line))
            else:
                dagster_logger.info(log_line.get("event", log_line))
        except json.decoder.JSONDecodeError:
            dagster_logger.info(log_line_raw)

        await asyncio.sleep(0)


@lru_cache
def task_op_factory(task: str) -> OpDefinition:
    """
    This factory is cached to make sure the same tasks can be reused in the
    same repository.
    """

    @op(
        name=generate_dagster_name(task),
        description=f"Run `{task}` using Meltano.",
        ins={"after": In(Nothing)},
        tags={"kind": "meltano"},
        required_resource_keys={"meltano"},
    )
    def dagster_op(context: OpExecutionContext):
        meltano_resource: MeltanoResource = context.resources.meltano
        meltano_resource.meltano_invoker.run_and_log(
            "run",
            log_processor,
            task.split(),
        )

    return dagster_op


class Job:
    def __init__(self, meltano_job: dict, meltano_invoker: MeltanoInvoker) -> None:
        self.name = meltano_job["job_name"]
        self.tasks = meltano_job["tasks"]
        self.meltano_invoker = meltano_invoker

    @property
    def dagster_name(self) -> str:
        return generate_dagster_name(self.name)

    @property
    def dagster_job(self) -> JobDefinition:
        # We need to import the `meltano_resource` here to prevent circular imports.
        from dagster_meltano.meltano_resource import meltano_resource

        @job(
            name=self.dagster_name,
            description=f"Runs the `{self.name}` job from Meltano.",
            resource_defs={"meltano": meltano_resource},
        )
        def dagster_job():
            meltano_task_done = None
            for task in self.tasks:
                meltano_task_op = task_op_factory(task)
                if meltano_task_done:
                    meltano_task_done = meltano_task_op(meltano_task_done)
                else:
                    meltano_task_done = meltano_task_op()

        return dagster_job
