"""Meltano Dagster extension."""
from __future__ import annotations

import os
import pkgutil
import subprocess
import sys
from pathlib import Path
from typing import Any

import structlog
from meltano.edk import models
from meltano.edk.extension import ExtensionBase
from meltano.edk.process import Invoker, log_subprocess_error

log = structlog.get_logger()


class Dagster(ExtensionBase):
    """Extension implementing the ExtensionBase interface."""

    def __init__(self) -> None:
        """Initialize the extension."""
        self.invokers = {
            "dagster": Invoker("dagster"),
            "dagit": Invoker("dagit"),
            "meltano": Invoker("meltano"),
        }

    def initialize(self, force: bool = False) -> None:
        self.invokers["meltano"].run_and_log("dragon")
        return super().initialize(force)

    def invoke(self, invoker: Invoker, command_name: str | None, *command_args: Any) -> None:
        """Invoke the underlying cli, that is being wrapped by this extension.

        Args:
            command_name: The name of the command to invoke.
            command_args: The arguments to pass to the command.
        """
        try:
            invoker.run_and_log(command_name, *command_args)
        except subprocess.CalledProcessError as err:
            log_subprocess_error(f"{invoker.bin} {command_name}", err, "Dagster invocation failed")
            sys.exit(err.returncode)

    def describe(self) -> models.Describe:
        """Describe the extension.

        Returns:
            The extension description
        """
        # TODO: could we auto-generate all or portions of this from typer instead?
        return models.Describe(
            commands=[
                models.ExtensionCommand(name="dagster_extension", description="extension commands"),
                models.InvokerCommand(name="dagster_invoker", description="pass through invoker"),
            ]
        )

    def get_invoker_by_name(self, invoker_name: str) -> Invoker:
        return self.invokers[invoker_name]

    def pass_through_invoker(
        self, invoker_name: str, logger: structlog.BoundLogger, *command_args: Any
    ) -> None:
        """Pass-through invoker.

        This method is used to invoke the wrapped CLI with arbitrary arguments.
        Note this method will hard exit the process if an unhandled exception is
        encountered.

        Args:
            invoker_name: The name of the invoker, currently "dagster" or "dagit".
            logger: The logger to use in the event an exception needs to be logged.
            *command_args: The arguments to pass to the command.
        """
        logger.debug(
            "pass through invoker called",
            command_args=command_args,
        )
        try:
            self.pre_invoke()
        except Exception:
            logger.exception(
                "pre_invoke failed with uncaught exception, please report to maintainer"
            )
            sys.exit(1)

        try:
            invoker = self.get_invoker_by_name(invoker_name)
            self.invoke(invoker, None, command_args)
        except Exception:
            logger.exception("invoke failed with uncaught exception, please report to maintainer")
            sys.exit(1)

        try:
            self.post_invoke()
        except Exception:
            logger.exception(
                "post_invoke failed with uncaught exception, please report to maintainer"  # noqa: E501
            )
            sys.exit(1)
