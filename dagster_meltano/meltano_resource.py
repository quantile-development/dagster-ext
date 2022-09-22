from typing import Optional

from dagster_meltano.utils import Singleton


class MeltanoResource(metaclass=Singleton):
    def __init__(self, project_dir: str, meltano_bin: Optional[str] = "meltano"):
        self.project_dir = project_dir
        self.meltano_bin = meltano_bin
