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

        ret = shell.run_cmd(f"rm {cpio} {zip}")
        if not ret:
            logger.error("Failed to extract initramfs")
            return None

        return self.mount_point


    def umount(self) -> None:
        cpio = "tmpramfs.cpio.gz"
        logger.debug(f"Path {self.path}")
        if Path(cpio).exists():
            logger.error("initramfs.cpio exists, exiting to prevent data loss")
            return

        ret = shell.run_cmd(f"cd {self.mount_point} && find . | cpio -o -H newc -R root:root | {shell.get_zip_cmd()} -9 > ../{cpio}")
        if not ret:
            logger.error("Failed to pack initramfs")
            return None

        ret = shell.run_cmd(f"cp \"{cpio}\" \"{self.path}\"")
        if not ret:
            logger.error("Failed to copy final image")
            return None

        shell.run_cmd(f"rm {cpio}")
        if self.tempdir:
            self.tempdir.cleanup()


    @staticmethod
    def can_handle(path:str) -> bool:
        return path.endswith(".cpio.gz")
