from pathlib import Path
from log import logger



# Base image is just a path to a directory
class Image:

    path:Path = Path()
    name:str = "Directory"

    def __init__(self, path:Path):
        self.path = path

    def mount(self) -> Path|None:
        return self.path

    def umount(self) -> None:
        pass


    @staticmethod
    def can_handle(path:Path) -> bool:
        return path.is_dir()


import image_ext4
IMAGE_TYPES = [
    image_ext4.ImageExt4,
    Image
]

def find_image(path:Path) -> Image|None:
    for image_type in IMAGE_TYPES:
        if image_type.can_handle(path):
            logger.info("Using %s image type", image_type.name)
            return image_type(path)
    return None
