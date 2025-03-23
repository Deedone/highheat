from log import logger
import config
import sys
import subprocess
import time



def run_cmd(command: str) -> bool:
    logger.info("Running command: %s", command)
    time.sleep(5)
    
    if config.conf.dryrun:
        return True
    try:
        result = subprocess.run(command, shell=True, check=True, stdin=sys.stdin)
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        logger.error("Command '%s' failed with error: %s", command, e.stderr.decode('utf-8'))
        return False
