from pathlib import Path
import tempfile

from highheat import image
from highheat import shell
from highheat.log import logger

from highheat.image_ramfs_gz import ImageRamfsGZ

class ImageUImage(image.Image):
    name:str = "ramfs u-boot"
    mount_point:Path = Path()
    tempdir:tempfile.TemporaryDirectory | None = None
    unpacker:ImageRamfsGZ | None = None
    mountable = True

    def __init__(self, path:Path):
        super().__init__(path)


    def mount(self) -> Path|None:
        self.tempdir = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.mount_point = Path(self.tempdir.name)

        zip = self.mount_point / "initramfs.zip"
        ret = shell.run_cmd(f"tail -c+65 < {self.path} > {zip}")
        if not ret:
            logger.error("Failed to extract initramfs")
            return None

        self.unpacker = ImageRamfsGZ(zip)
        unpacked = self.unpacker.mount()

        if not unpacked:
            logger.error("Failed to extract initramfs")
            return None
        self.mount_point = unpacked

        return self.mount_point


    def umount(self) -> bool:
        if not self.unpacker:
            logger.error("No unpacker available, cannot umount")
            return False

        ret = self.unpacker.umount()
        if not ret:
            logger.error("Failed to umount inner ramfs")
            return False

        packed = self.unpacker.path
        if not packed.exists():
            logger.fatal("No packed initramfs found, this should not happen please report")
            return False

        ret = shell.run_cmd(f"mkimage -A arm64 -C gzip -T ramdisk -n 'uInitramfs' -d {packed} {self.path}")
        if not ret:
            logger.error("Failed to pack initramfs")
            return False

        shell.run_cmd(f"rm {packed}")
        if self.tempdir:
            self.tempdir.cleanup()

        return True


    @staticmethod
    def can_handle(path:str) -> bool:
        return path.endswith("uInitramfs")
