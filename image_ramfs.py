import image
from pathlib import Path
import shell
import tempfile
from log import logger

# unpack() {
#     rm -rf ramfs
#     mkdir ramfs
#     cd ramfs
#     echo "Extracting"
#     tail -c+65 < ../uInitramfs > ./uInitramfs
#     cat uInitramfs | gunzip > initramfs.cpio
#     cpio -id < initramfs.cpio
#     rm initramfs.cpio uInitramfs
#     echo "Extracted to ./ramfs"
# }

# pack() {
#         cd ramfs
#         find . | cpio -o -H newc -R root:root | gzip -9 > ../initramfs.img
#         echo "Creating image"
#         mkimage -A arm64 -C gzip -T ramdisk -n "uInitramfs" -d ../initramfs.img ../uInitramfs
#         rm ../initramfs.img
#         cd ..

# }

class ImageRamfs(image.Image):
    name:str = "ramfs"
    mount_point:Path = Path()
    tempdir:tempfile.TemporaryDirectory | None = None

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
        cpio = "initramfs.cpio"
        if Path(cpio).exists():
            logger.error("initramfs.cpio exists, exiting to prevent data loss")
            return

        ret = shell.run_cmd(f"cd {self.mount_point} && find . | cpio -o -H newc -R root:root | gzip -9 > ../{cpio}")
        if not ret:
            logger.error("Failed to pack initramfs")
            return None

        ret = shell.run_cmd(f"mkimage -A arm64 -C gzip -T ramdisk -n 'uInitramfs' -d {cpio} {self.path}")
        if not ret:
            logger.error("Failed to pack initramfs")
            return None

        shell.run_cmd(f"rm {cpio}")
        # Cleanup files inside the unpacked folder so it can be deleted by tempdir
        shell.run_cmd(f"sudo rm -rf {self.mount_point}")
        if self.tempdir:
            self.tempdir.cleanup()

    @staticmethod
    def can_handle(path:Path) -> bool:
        return path.name == "uInitramfs"
