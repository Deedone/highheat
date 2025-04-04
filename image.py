from pathlib import Path
from log import logger
import shell


# Base image is just a path to a directory
class Image:

    path:Path = Path()
    name:str = "Directory"
    mountable:bool = False

    def __init__(self, path:Path):
        self.path = path

    def mount(self) -> Path|None:
        return self.path

    def umount(self) -> None:
        pass

    def install(self, src:Path, dst:Path) -> bool:
        if src.is_dir():
            ret = shell.run_cmd(f"cp -r {src}/* {dst}")
        else:
            ret = shell.run_cmd(f"cp {src} {dst}")
        return ret

    @staticmethod
    def can_handle(path:str) -> bool:
        # Check for parent in case of installing as a new file
        return True


import image_ext4
import image_ramfs
IMAGE_TYPES = [
    image_ext4.ImageExt4,
    image_ramfs.ImageRamfs,
    Image
]

def find_image(path:Path) -> Image|None:
    for image_type in IMAGE_TYPES:
        if image_type.can_handle(str(path)):
            logger.info("Using %s image type", image_type.name)
            return image_type(path)
    return None

def needs_mount(target: str) -> bool:
    for image_type in IMAGE_TYPES:
        if image_type.can_handle(target):
            logger.debug("needs_mount: %d from image %s", image_type.mountable, image_type.name)
            return image_type.mountable
    return False
