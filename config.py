from typing import List
import os
import yaml
from log import logger

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
            break


    return conf
