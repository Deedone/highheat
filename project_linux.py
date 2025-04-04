import project
import yocto
from pathlib import Path
from log import logger
from typing import List
import shell


#TODO: Convert to find_image, leave default deploy impl
class ProjectLinux(project.Project):

    supported_names = [
        "linux-renesas",
        "linux",
        "virtual/kernel"
    ]
    name:str = "Linux"

    def deploy_image(self, target:str) -> None:
        logger.debug("deploy %s to %s", self.projname, target)
        if not self.initialized:
            return

        deploydir = self.find_deploydir()

        if not deploydir or not deploydir.exists():
            logger.error("Deploy dir %s don't exist", deploydir)
            return

        image = deploydir / "Image"
        if not image.exists():
            logger.error("Image %s not found", image)
        mounted = self.prepare_target(target)

        if not mounted:
            logger.error("Prepare target failed")
            return

        ret = shell.run_cmd(f"sudo cp {image} {mounted}")
        if not ret:
            logger.error("Copy failed")
            return

        logger.info("%s: Deploy successful", self.projname)

        self.cleanup()

#TODO: Move file selection to a generic module
#TODO: Add caching for selections (and some flag to bypass it)
    def select_source(self, sources: List[Path]) -> Path | None:
        if len(sources) == 1:
            return sources[0]

        sources.sort()
        print(f"Found {len(sources)} dtb images, please select one:")

        for i, s in enumerate(sources):
            print(f"{i+1}: {s.name}")

        answer = input("Select one: ")
        try:
            answer = int(answer) - 1
            return sources[answer]
        except Exception:
            logger.error("Invalid input %s", answer)
            return None

    def deploy_dtb(self, target:str) -> None:
        logger.debug("deploy dtb %s to %s", self.projname, target)
        if not self.initialized:
            return

        deploydir = self.find_deploydir()

        if not deploydir or not deploydir.exists():
            logger.error("Deploy dir %s don't exist", deploydir)
            return

        sources = list(deploydir.glob("*.dtb"))

        for p in sources:
            if p.is_symlink():
                resolved = p.resolve()
                if resolved in sources:
                    sources.remove(p.resolve())

        image = self.select_source(sources)
        logger.debug("Selected %s", image)
        if not image:
            logger.error("No valid image selected")
            return

        mounted = self.prepare_target(target)
        if not mounted:
            logger.error("Prepare target failed")
            return

        ret = shell.run_cmd(f"sudo cp {image} {mounted}")
        if not ret:
            logger.error("Copy failed")
            return

        logger.info("%s: Deploy successful", self.projname)

        self.cleanup()

    def deploy(self, target:str) -> None:
        if target.endswith(".dtb"):
            self.deploy_dtb(target)
        else:
            self.deploy_image(target)


    @staticmethod
    def can_handle(target:str) -> bool:
        return target in ProjectLinux.supported_names
