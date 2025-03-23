from log import logger
import log
import config
import sys
import subprocess


def log_cmd(command: str) -> None:
    logger.info("Running command:%s %s",log.RESET, command)

def run_cmd(command: str) -> bool:
    if config.conf.confirmcmd:
        log_cmd(command)
        if not input("Continue? [y/N]: ").lower() in 'yY':
            return False
    else:
        log_cmd(command)
    
    if config.conf.dryrun:
        return True
    try:
        result = subprocess.run(command, shell=True, check=True, stdin=sys.stdin)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error("Command '%s' failed with error: %s", command, e.stderr.decode('utf-8'))
        return False
