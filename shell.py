from log import logger
import log
import config
import sys
import subprocess
import time
from pathlib import Path
from datetime import datetime
import shutil
import halo
import halo.cursor as cursor


def log_cmd(command: str) -> None:
    logger.info("Running command:%s %s",log.RESET, command)

prev_time = 0
def is_new_frame(interval: float):
    global prev_time
    curr_time = time.time()
    if curr_time - prev_time > interval:
        prev_time = curr_time
        return True
    return False

def trim_left(string: str, length: int) -> str:
    if len(string) <= length:
        return string
    elif length <= 3:
        return string[-length:]
    else:
        return "..." + string[-(length-3):]

def status_logs(proc, cmdline:str):
    terminal_width = shutil.get_terminal_size().columns
    filler = " " * terminal_width
    cursor.hide()
    h = halo.Halo(text=trim_left(cmdline, terminal_width - 5), spinner="dots")
    spinnertext = h.frame()
    for line in iter(proc.stdout.readline, ''):
        if is_new_frame(0.1):
            spinnertext = h.frame()
        print(filler + "\r", end="") # Clear previous spinner line
        print(line,end="") 
        print(spinnertext + "\r", end="")
        
    cursor.show()
    spinnertext = h.frame()
    print(filler + "\r") # Clear previous spinner line
    sys.stdout.flush() 
    

def run_cmd(command: str) -> bool:
    log_cmd(command)
    if config.conf.confirmcmd and not config.conf.dryrun:
        if not input("Continue? [y/N]: ").lower() in 'yY':
            return False

    if config.conf.dryrun:
        return True
    try:
        result = subprocess.Popen(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        status_logs(result, command)
        
        for line in iter(result.stderr.readline, ''):
            print(line,end="")
            
        return result.wait() == 0
    except subprocess.CalledProcessError as e:
        logger.error("Command '%s' failed with error: %d", command, e.returncode)
        return False

def try_delete(p:Path):
    logger.debug("p exists %d p is_dir %d", p.exists(), p.is_dir())
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
                try_delete(file)
