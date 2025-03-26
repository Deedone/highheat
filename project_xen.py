import project
import yocto
from pathlib import Path
from log import logger
from typing import List
import shell


class ProjectXen(project.Project):

    supported_names = [
        "xen"
    ]
    name:str = "Xen"

    def find_image(self) -> Path | None:
        deploydir = self.workdir / f"deploy-{self.projname}"

        if not deploydir.exists():
            logger.error("Deploy dir %s don't exist", deploydir)
            return

        return deploydir / "xen-uImage"

    @staticmethod
    def can_handle(target:str) -> bool:
        return target in ProjectXen.supported_names
