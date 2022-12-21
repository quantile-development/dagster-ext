"""Meltano Dagster extension."""
from __future__ import annotations

import ast
import os
import pkgutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

import structlog
import typer
from cookiecutter.main import cookiecutter
from rich import print
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Confirm, Prompt

import files_dagster_ext
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
            "cloud": Invoker("dagster-cloud"),
            "docker": Invoker("docker"),
            "meltano": Invoker("meltano", env={**os.environ, "MELTANO_ENVIRONMENT": ""}),
        }

    @property
    def utility_name(self) -> str:
        return os.getenv("MELTANO_UTILITY_NAME", "dagster")

    @property
    def dagster_home(self) -> Path:
        return Path(os.getenv("DAGSTER_HOME"))

    @property
    def cloud_env_variables(self) -> List[str]:
        if not "DAGSTER_CLOUD_ENV_VARIABLES" in os.environ:
            return []

        return ast.literal_eval(os.environ["DAGSTER_CLOUD_ENV_VARIABLES"])

    @property
    def cookiecutter_template_dir(self) -> str:
        """
        Find the location of the files extention.
        This houses the cookiecutter project.
        """
        return Path(files_dagster_ext.__path__._path[0]) / "dagster"

    def set_meltano_config(self, description: str, config_name: str, config_value: str) -> None:
        spinner = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )

        with spinner as progress:
            progress.add_task(description=description, total=None)
            self.get_invoker_by_name("meltano").run(
                "config",
                self.utility_name,
                "set",
                config_name,
                config_value,
            )

    def initialize(self, force: bool = False) -> None:
        repository_dir = os.path.expandvars("$MELTANO_PROJECT_ROOT/orchestrate/dagster")
        repository_dir = Path(repository_dir)

        repository_name = Prompt.ask(
            "What would you like your Dagster repository to be called?",
            default="meltano",
        )

        repository_name = repository_name.replace("-", "_").replace(" ", "-")

        # setup_cloud = Confirm.ask(
        #     "Do you want to setup Dagster Cloud Serverless?",
        #     default=True,
        # )

        # if setup_cloud:
        #     cloud_organization = Prompt.ask(
        #         "What is your Dagster Cloud organization name?",
        #         default=os.getenv("DAGSTER_CLOUD_ORGANIZATION"),
        #     )
        #     self.set_meltano_config(
        #         description="Setting Dagster Cloud organization",
        #         config_name="cloud_organization",
        #         config_value=cloud_organization,
        #     )

        #     cloud_api_token = Prompt.ask(
        #         "What is your Dagster Cloud api token?",
        #         password=True,
        #     )
        #     self.set_meltano_config(
        #         description="Setting Dagster Cloud organization",
        #         config_name="cloud_api_token",
        #         config_value=cloud_api_token,
        #     )

        #     cloud_location_name = Prompt.ask(
        #         "What is your Dagster Cloud location name?",
        #         default=os.getenv("DAGSTER_CLOUD_LOCATION_NAME", "meltano"),
        #     )
        #     self.set_meltano_config(
        #         description="Setting Dagster Cloud location name",
        #         config_name="cloud_location_name",
        #         config_value=cloud_location_name,
        #     )

        # TODO: Create a dockerignore here

        # dbt_installed = Confirm.ask(
        #     "Do you have DBT installed?",
        #     default=True,
        # )

        # if dbt_installed:
        #     dbt_plugin = Prompt.ask(
        #         "Which DBT plugin do you have installed?",
        #         choices=["postgres", "snowflake", "bigquery", "redshift"],
        #     )
        #     print(
        #         "[blue]Make sure you define the DBT environment variables in the Dagster utility.[/blue]"
        #     )
        # else:
        #     dbt_plugin = None

        dbt_plugin = None

        cookiecutter_config = {
            "project_name": repository_dir.name,
            "repository_name": repository_name,
            "dbt_plugin": dbt_plugin,
        }

        cookiecutter(
            template=str(self.cookiecutter_template_dir),
            no_input=True,
            extra_context=cookiecutter_config,
            output_dir=str(repository_dir.parent),
            overwrite_if_exists=True,
        )

        print("[green]Successfully initialized your Dagster project![/green]")
        print("[green]Start Dagit by running `meltano invoke dagster:start`[/green]")
        # print("[blue]Or deploy by running `meltano invoke dagster:deploy`[/blue]")

    def get_env_value(self, env_variable: str) -> str:
        try:
            return os.environ[env_variable]
        except KeyError:
            raise Exception(f"Could not find environment variable with the name: {env_variable}")

    def env_flags(self, cloud_env_variables: List[str]) -> List[str]:
        """Create --env flags for the dagster cloud deploy command. We try
        to fetch the value from the current environment.

        Args:
            cloud_env_variables (List[str]): A list of environments values to pass through.

        Returns:
            List[str]: A list of --env flags.
        """
        for env_variable in cloud_env_variables:
            yield "--env"
            yield f"{env_variable}='{self.get_env_value(env_variable)}'"

    def deploy(self, root: str, python_file: str, docker_file: str, location_name: str) -> None:
        pre_build_image_name = "dagster-meltano"
        docker_invoker = self.get_invoker_by_name("docker")
        dagster_cloud_invoker = self.get_invoker_by_name("cloud")
        env_flags = self.env_flags(self.cloud_env_variables)

        build_args = [
            "-f",
            docker_file,
            "-t",
            pre_build_image_name,
            root,
        ]

        docker_invoker.run_and_log("build", build_args)

        deploy_args = [
            "deploy",
            "-f",
            python_file,
            "--location-name",
            location_name,
            "--base-image",
            pre_build_image_name,
            *env_flags,
            root,
        ]

        dagster_cloud_invoker.run_and_log("serverless", deploy_args)

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
        return models.Describe(
            commands=[
                models.ExtensionCommand(
                    name="dagster_extension",
                    description="extension commands",
                ),
                models.InvokerCommand(
                    name="dagster_invoker",
                    description="pass through invoker for dagster",
                ),
                models.InvokerCommand(
                    name="dagit_invoker",
                    description="pass through invoker for dagit",
                ),
                models.InvokerCommand(
                    name="cloud_invoker",
                    description="pass through invoker for dagster cloud",
                ),
            ]
        )

    def get_invoker_by_name(self, invoker_name: str) -> Invoker:
        return self.invokers[invoker_name]

    def pre_invoke(self, invoke_name: str | None, *invoke_args: Any) -> None:
        """Called before the extension is invoked.

        Args:
            invoke_name: The name of the command that will be passed to invoke.
            *invoke_args: The arguments that will be passed to invoke.
        """
        self.dagster_home.mkdir(parents=True, exist_ok=True)

    def pass_through_invoker(
        self, invoker_name: str, logger: structlog.BoundLogger, *command_args: Any
    ) -> None:
        """Pass-through invoker.

        This method is used to invoke the wrapped CLI with arbitrary arguments.
        Note this method will hard exit the process if an unhandled exception is
        encountered.

        Args:
            invoker_name: The name of the invoker, currently "dagster", "dagit" or "cloud".
            logger: The logger to use in the event an exception needs to be logged.
            *command_args: The arguments to pass to the command.
        """
        logger.debug(
            "pass through invoker called",
            command_args=command_args,
        )
        try:
            self.pre_invoke(None)
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
            self.post_invoke(None)
        except Exception:
            logger.exception(
                "post_invoke failed with uncaught exception, please report to maintainer"  # noqa: E501
            )
            sys.exit(1)


if __name__ == "__main__":
    path = files_dagster_ext.__path__
