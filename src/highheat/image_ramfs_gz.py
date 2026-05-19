from pathlib import Path
import tempfile

from highheat import image
from highheat import shell
from highheat.log import logger

class ImageRamfsGZ(image.Image):
    name:str = "ramfs.cpio.gz"
    mount_point:Path = Path()
    tempdir:tempfile.TemporaryDirectory | None = None
    mountable = True

    def __init__(self, path:Path):
        super().__init__(path)


    def mount(self) -> Path|None:
        self.tempdir = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.mount_point = Path(self.tempdir.name)

        zip = self.path

        cpio = self.mount_point / "initramfs.cpio"
        ret = shell.run_cmd(f"cat {zip} | gunzip > {cpio}")
        if not ret:
            logger.error("Failed to extract initramfs")
            return None

        ret = shell.run_cmd(f"cd {self.mount_point} && cpio -id < {cpio}")
        if not ret:
            logger.error("Failed to extract initramfs")
            return None

        ret = shell.run_cmd(f"rm {cpio}")
        if not ret:
            logger.error("Failed to extract initramfs")
            return None

        return self.mount_point


    def umount(self) -> bool:
        cpio = "tmpramfs.cpio.gz"
        logger.debug(f"Path {self.path}")
        if Path(cpio).exists():
            logger.error("initramfs.cpio exists, exiting to prevent data loss")
            return False

        ret = shell.run_cmd(f"cd {self.mount_point} && find . | cpio --reproducible -o -H newc -R root:root | {shell.get_zip_cmd()} --rsyncable > ../{cpio}")
        if not ret:
            logger.error("Failed to pack initramfs")
            return False

        ret = shell.run_cmd(f"mv \"{cpio}\" \"{self.path}\"")
        if not ret:
            logger.error("Failed to move final image")
            return False

        if self.tempdir:
            self.tempdir.cleanup()

        return True


    @staticmethod
    def can_handle(path:str) -> bool:
        return path.endswith(".cpio.gz")
