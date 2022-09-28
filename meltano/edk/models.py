"""Various models used to describe extensions."""
from typing import List

from pydantic import BaseModel


class Command(BaseModel):
    """Describe a generic runnable command."""

    name: str
    description: str
    commands: List[str] = []
    pass_through_cli: bool = False


class ExtensionCommand(Command):
    """Describes an extension command."""

    description = "The extension cli"
    pass_through_cli: bool = False
    commands: List[str] = [
        "describe",
        "invoke",
        "pre_invoke",
        "post_invoke",
        "initialize",
    ]


class InvokerCommand(Command):
    """Describes an invoker style command."""

    description = "The pass through invoker cli"
    pass_through_cli: bool = True
    commands: List[str] = [":splat"]


class Describe(BaseModel):
    """Describes what commands and capabilities the extension provides."""

    commands: List[Command]
