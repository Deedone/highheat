from pathlib import Path
from log import logger
from transport import Transport
import shell
import config




class TransportRemoteRsync(Transport):

    target:str = ""
    host:str = ""
    name:str = "Remote rsync"


    def __init__(self, target:str):
        self.host, self.target = target.split(":")

    def download(self) -> Path|None:

        dldir = Path(config.conf.dldir)
        if not dldir.exists():
            dldir.mkdir(parents=True)

        
        ret = shell.run_cmd(f"rsync -avhP --delete {self.host}:{self.target} {dldir}")
        if not ret:
            logger.error("Failed to download %s:%s", self.host, self.target)
            return None

        return dldir / Path(self.target).name
        

    def upload(self) -> bool:
        dldir = Path(config.conf.dldir)
        target_name = Path(self.target).name

        if not dldir.exists():
            logger.error("Download directory %s does not exist", dldir)
            return False

        ret = shell.run_cmd(f"rsync -avhP {dldir / target_name} {self.host}:{self.target}")

        if not ret:
            logger.error("Failed to upload %s:%s", self.host, self.target)
            return False
        
        return True


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
