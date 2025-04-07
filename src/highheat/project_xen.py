from pathlib import Path


from highheat import project
from highheat.log import logger


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
