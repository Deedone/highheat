from log import logger
import log
import config
import sys
import subprocess


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
