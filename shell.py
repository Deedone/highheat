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
import pty
import os
import select
import fcntl


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

def direct_logs(cmdlin:str, master:int):
    while True:
        ready, _, _ = select.select([master], [], [], 0.1)
        if master in ready:
            try:
                data = os.read(master, 1024).decode('utf-8')
            except OSError:
                break
            print(data,end="")
    

def status_logs(cmdline:str, master:int):
    terminal_width = shutil.get_terminal_size().columns
    filler = " " * terminal_width
    cursor.hide()
    h = halo.Halo(text=trim_left(cmdline, terminal_width - 5), spinner="dots")
    spinnertext = h.frame()
    end = ""
    while True:
        ready, _, _ = select.select([master], [], [], 0.1)
        if master in ready:
            try:
                data = os.read(master, 1024).decode('utf-8')
            except OSError:
                break
            if is_new_frame(0.1):
                spinnertext = h.frame()
            print(filler + "\r", end="") # Clear previous spinner line
            if end == "\n":
                print("\033[A", end="")
            end = "" if data.endswith("\n") else "\n"
            print(data,end=end)
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
        master, slave = pty.openpty()
        result = subprocess.Popen(command, shell=True, text=True, stdout=slave, stderr=slave, bufsize=0)
        os.close(slave)
        flags = fcntl.fcntl(master, fcntl.F_GETFL)
        fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)
        
        if sys.stdout.isatty():
            status_logs(command, master)
        else:
            direct_logs(command, master)
        
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
