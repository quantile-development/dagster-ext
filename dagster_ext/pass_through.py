"""Passthrough shim for Dagster extension."""
import sys

import structlog
from meltano.edk.logging import pass_through_logging_config

from dagster_ext.extension import Dagster


def pass_through_cli_dagster() -> None:
    """Pass through CLI entry point for Dagster."""
    pass_through_logging_config()
    ext = Dagster()
    ext.pass_through_invoker(
        "dagster",
        structlog.getLogger("dagster_invoker"),
        *sys.argv[1:] if len(sys.argv) > 1 else [],
    )


def pass_through_cli_dagit() -> None:
    """Pass through CLI entry point for Dagit."""
    pass_through_logging_config()
    ext = Dagster()
    ext.pass_through_invoker(
        "dagit",
        structlog.getLogger("dagit_invoker"),
        *sys.argv[1:] if len(sys.argv) > 1 else [],
    )
