from pathlib import Path
from typing import List

from highheat.log import logger
from highheat import project
from highheat import config
from subprocess import run

#TODO: Convert to find_image, leave default deploy impl
class ProjectInteractive(project.Project):

    projname:str = "interactive"

    def __init__(self):
        self.initialized = True

    def deploy(self, target:str) -> bool | None:
        mounted = self.prepare_target(target)

        if not mounted:
            logger.error("Prepare target failed")
            return False

        if mounted.is_dir():
            logger.info("Close this shell (Ctrl-D) to finish editing")
            ret = run(f"cd {mounted} && $SHELL", shell=True)
        elif str(mounted).endswith(".dtb"):
            logger.warning("Starting inner project for dtb unpacking\n") #TODO FIXME
            inner = ProjectInteractive()
            ret = inner.deploy(str(mounted))
        else:
            editor = config.conf.ieditorpath
            logger.info("Close the editor (%s) to finish editing", editor)
            run(f"{editor} {mounted}", shell=True)
            ret = True

        if not ret:
            return False


        logger.info("Image editing done")

        self.cleanup()

        return True

    @staticmethod
    def can_handle(target:str) -> bool:
        return True
