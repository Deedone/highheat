import image
from pathlib import Path
import shell
import tempfile
from log import logger


class ImageExt4(image.Image):
    name:str = "Ext4"
    mount_point:Path = Path()
    tempdir:tempfile.TemporaryDirectory | None = None
    mounted:bool = False


    def __init__(self, path:Path):
        super().__init__(path)


    def __del__(self):
        self.umount()
        if self.tempdir:
            self.tempdir.cleanup()


    def mount(self) -> Path|None:
        self.tempdir = tempfile.TemporaryDirectory(dir=Path.cwd())
        self.mount_point = Path(self.tempdir.name)
        ret = shell.run_cmd(f"sudo mount {self.path} {self.mount_point}")

        if not ret:
            logger.error("Failed to mount %s", self.path)
            return None

        self.mounted = True
        return self.mount_point


    def umount(self) -> None:
        if self.mounted:
            shell.run_cmd(f"sudo umount {self.mount_point}")
            self.mounted = False

        if self.tempdir:
            self.tempdir.cleanup()


    @staticmethod
    def can_handle(path:Path) -> bool:
        return path.suffix == ".ext4"
