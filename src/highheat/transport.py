from pathlib import Path

from highheat import shell
from highheat.log import logger

class Transport:

    target:str = ""
    name:str = "Local"


    def __init__(self, target:str):
        self.target = target


    def download(self) -> Path|None:
        return Path(self.target)


    def upload(self) -> bool:
        return True
        
    def install(self, src:Path, dst:str) -> bool:
        if src.is_dir():
            ret = shell.run_cmd(f"cp -r {src}/* {dst}")
        else:
            ret = shell.run_cmd(f"cp {src} {dst}")
        return ret


    @staticmethod
    def can_handle(_target:str) -> bool:
        return True


from highheat import transport_rsync
TRANSPORT_TYPES = [
    transport_rsync.TransportRemoteRsync,
    Transport
]

def find_transport(target:str) -> Transport|None:
    for transport_type in TRANSPORT_TYPES:
        if transport_type.can_handle(target):
            logger.info("Using %s transport type", transport_type.name)
            return transport_type(target)
    return None
