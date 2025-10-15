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

    def deploy(self, target:str) -> None:
        mounted = self.prepare_target(target)

        if not mounted:
            logger.error("Prepare target failed")
            return

        if mounted.is_dir():
            logger.info("Close this shell (Ctrl-D) to finish editing")
            ret = run(f"cd {mounted} && $SHELL", shell=True)

        else:
            editor = config.conf.ieditorpath
            logger.info("Close the editor (%s) to finish editing", editor)
            ret = run(f"{editor} {mounted}", shell=True)

        if not ret:
            logger.error("Copy failed")
            return

        logger.info("Image editing done")

        self.cleanup()

    @staticmethod
    def can_handle(target:str) -> bool:
        return True
