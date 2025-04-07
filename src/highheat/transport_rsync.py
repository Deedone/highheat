from pathlib import Path

from highheat import shell
from highheat import config
from highheat.log import logger
from highheat.transport import Transport




class TransportRemoteRsync(Transport):

    target:str = ""
    host:str = ""
    name:str = "Remote rsync"


    def __init__(self, target:str):
        self.host, self.target = target.split(":")

    def download(self) -> Path|None:
        dldir = Path(config.conf.dldir)
        target = dldir / Path(self.target).name
        if not dldir.exists():
            dldir.mkdir(parents=True)


        ret = shell.run_cmd(f"rsync -avhzP --delete {self.host}:{self.target} {target}")
        if not ret:
            if target.exists() and target.is_dir():
                logger.warn("Failed to download all files from %s:%s", self.host, self.target)
            else:
                logger.error("Failed to download %s:%s", self.host, self.target)
                return None

        return target


    def upload(self) -> bool:
        dldir = Path(config.conf.dldir)
        target_name = Path(self.target).name
        source = dldir / target_name

        if not dldir.exists():
            logger.error("Download directory %s does not exist", dldir)
            return False

        if source.is_dir():
            ret = shell.run_cmd(f"rsync -avhP --no-owner --no-group --no-times {source}/ {self.host}:{self.target}")
        else:
            ret = shell.run_cmd(f"rsync -avhP {source} {self.host}:{self.target}")

        if not ret:
            logger.error("Failed to upload %s:%s", self.host, self.target)
            return False

        return True
        
    
    def install(self, src:Path, dst:str) -> bool:
        if src.is_symlink():
            src = src.resolve()
            
        if src.is_dir():
            ret = shell.run_cmd(f"rsync -avhP --no-owner --no-group --no-times {src}/ {dst}")
        else:
            ret = shell.run_cmd(f"rsync -avhP {src} {dst}")

        if not ret:
            logger.error("Failed to upload %s:%s", self.host, self.target)
        return ret

    @staticmethod
    def can_handle(target:str) -> bool:
        return ":" in target


TRANSPORT_TYPES = [
    Transport
]

def find_transport(target:str) -> Transport|None:
    for transport_type in TRANSPORT_TYPES:
        if transport_type.can_handle(target):
            logger.info("Using %s transport type", transport_type.name)
            return transport_type(target)
    return None
