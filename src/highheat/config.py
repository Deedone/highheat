from typing import List
import os
import yaml
from datetime import timedelta

from highheat.log import logger

CONFIG_PATHS:List[str] = [
    os.path.join(os.getenv('XDG_CONFIG_HOME', os.path.expanduser('~/.config')), 'highheat.yaml'),
    os.path.expanduser('~/.config/highheat.yaml'),
    'highheat.yaml',
]

class Config:
    editorpath:str = 'vim'
    verbose:bool = False
    dryrun:bool = False
    confirmcmd:bool = True
    dldir:str = os.path.expanduser('~/.cache/highheat')
    dldir_cleanup_interval:timedelta = timedelta(days=7)

    def __str__(self) -> str:
        return f"editorpath: {self.editorpath} confirmcmd: {self.confirmcmd}"

conf = Config()

def load() -> Config:
    for path in CONFIG_PATHS:
        if os.path.exists(path):
            logger.debug("loading config from %s", path)
            with open(path, "r") as f:
                config = yaml.safe_load(f)
                if "editor" in config:
                    conf.editorpath = config["editor"]
                if "confirm" in config:
                    conf.confirmcmd = config["confirm"]
                if "dldir" in config:
                    conf.dldir = os.path.expanduser(config["dldir"])
                if "dldir_cleanup_interval" in config:
                    conf.dldir_cleanup_interval = timedelta(days=config["dldir_cleanup_interval"])
            break


    return conf
