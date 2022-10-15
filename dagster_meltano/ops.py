from __future__ import annotations

import asyncio
import json
from functools import lru_cache
from typing import TYPE_CHECKING, Optional

from dagster import (
    In,
    Nothing,
    OpDefinition,
    OpExecutionContext,
    get_dagster_logger,
    op,
)

from dagster_meltano.utils import generate_dagster_name

if TYPE_CHECKING:
    from dagster_meltano.meltano_resource import MeltanoResource

dagster_logger = get_dagster_logger()


async def log_processor(reader: asyncio.streams.StreamReader, log_type: str) -> None:
    """Parse the Meltano logs, and try to print cleaner logs to Dagster.

    Args:
        reader: The stream reader to read from.
        log_type: The type of logging coming in, either stderr or stdout.
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
def meltano_run_op(command: str) -> OpDefinition:
    """
    Run `meltano run <command>` using a Dagster op.

    This factory is cached to make sure the same commands can be reused in the
    same repository.
    """

    @op(
        name=generate_dagster_name(command),
        description=f"Run `{command}` using Meltano.",
        ins={"after": In(Nothing)},
        tags={"kind": "meltano"},
        required_resource_keys={"meltano"},
    )
    def dagster_op(context: OpExecutionContext):
        meltano_resource: MeltanoResource = context.resources.meltano
        meltano_resource.meltano_invoker.run_and_log(
            "run",
            log_processor,
            command.split(),
        )

    return dagster_op


@op(
    name=generate_dagster_name("meltano install"),
    description=f"Install all Meltano plugins",
    ins={"after": In(Nothing)},
    tags={"kind": "meltano"},
    required_resource_keys={"meltano"},
)
def meltano_install_op(context: OpExecutionContext):
    """
    Run `meltano install` using a Dagster op.
    """
    meltano_resource: MeltanoResource = context.resources.meltano
    meltano_resource.meltano_invoker.run_and_log(
        "install",
        log_processor,
    )
