from pathlib import Path
import time

from highheat import image
from highheat import shell
from highheat.log import logger

class ImageDtb(image.Image):
    name:str = "dtb"
    mount_point:Path = Path()
    mountable = True

    def __init__(self, path:Path):
        super().__init__(path)


    def mount(self) -> Path|None:

        dtb = self.path
        self.mount_point = dtb.with_suffix('.dts')

        if self.mount_point.exists():
            logger.warning("Decompiled DTB is already present, reusing it to preserve changes");
            logger.warning("Remove %s if you want to recompile from DTB", self.mount_point)
            time.sleep(2)
            return self.mount_point

        ret = shell.run_cmd(f"dtc -I dtb -O dts {self.path} > {self.mount_point}")
        if not ret:
            logger.error("Failed to extract dtb")
            return None

        return self.mount_point


    def umount(self) -> bool:
        dts = self.mount_point

        ret = shell.run_cmd(f"dtc -I dts -O dtb {dts} > {self.path}")
        if not ret:
            logger.error("Failed to pack dtb")
            return False

        return True

    @staticmethod
    def can_handle(path:str) -> bool:
        return path.endswith(".dtb")
