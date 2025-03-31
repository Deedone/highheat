from log import logger
import log
import config
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import shutil


def log_cmd(command: str) -> None:
    logger.info("Running command:%s %s",log.RESET, command)

def run_cmd(command: str) -> bool:
    log_cmd(command)
    if config.conf.confirmcmd and not config.conf.dryrun:
        if not input("Continue? [y/N]: ").lower() in 'yY':
            return False

    if config.conf.dryrun:
        return True
    try:
        result = subprocess.run(command, shell=True, check=True, stdin=sys.stdin)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error("Command '%s' failed with error: %d", command, e.returncode)
        return False

def try_delete(p:Path):
    try:
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
    except Exception as e:
        logger.error("Failed to delete %s: %s", p, e)

def cleanup_dldir():
    logger.info("Checking dldir for old files")
    dldir = Path(config.conf.dldir)
    if not dldir.exists():
        return

    now = datetime.now()
    for file in dldir.iterdir():
        if file.exists():
            age = now - datetime.fromtimestamp(file.stat().st_mtime)
            if age > config.conf.dldir_cleanup_interval:
                file.unlink()
