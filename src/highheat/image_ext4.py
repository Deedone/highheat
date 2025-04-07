from pathlib import Path
import tempfile

from highheat import image
from highheat import shell
from highheat.log import logger


class ImageExt4(image.Image):
    name:str = "Ext4"
    mount_point:Path = Path()
    tempdir:tempfile.TemporaryDirectory | None = None
    mounted:bool = False
    mountable = True


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

    def install(self, src:Path, dst:Path) -> bool:
        if src.is_dir():
            ret = shell.run_cmd(f"sudo cp -r {src}/* {dst}")
        else:
            ret = shell.run_cmd(f"sudo cp {src} {dst}")
        return ret

    def umount(self) -> None:
        if self.mounted:
            shell.run_cmd(f"sudo umount {self.mount_point}")
            self.mounted = False

        if self.tempdir:
            self.tempdir.cleanup()


    @staticmethod
    def can_handle(path:str) -> bool:
        return path.endswith(".ext4")
