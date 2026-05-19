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

from highheat import log
from highheat.log import logger
from highheat import config

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

def direct_logs(cmdlin:str, master:int, errmaster:int):
    while True:
        ready, _, _ = select.select([master, errmaster], [], [], 0.1)
        if master in ready:
            try:
                data = os.read(master, 1024).decode('utf-8')
            except OSError:
                break
            print(data,end="")

        if errmaster in ready:
            try:
                data = os.read(errmaster, 1024).decode('utf-8')
            except OSError:
                break
            print(data,end="")


def status_logs(cmdline:str, master:int, errmaster:int) -> str:
    terminal_width = shutil.get_terminal_size().columns
    filler = " " * terminal_width
    cursor.hide()
    h = halo.Halo(text=trim_left(cmdline, terminal_width - 5), spinner="dots")
    errbuf = ""

    spinnertext = h.frame()
    end = ""
    while True:
        err = False
        data = ""
        ready, _, _ = select.select([master, errmaster], [], [], 0.1)
        if is_new_frame(0.1):
            spinnertext = h.frame()
        if errmaster in ready:
            try:
                err = True
                data += os.read(errmaster, 1024).decode('utf-8')
                errbuf += data
            except OSError:
                break

        if master in ready:
            try:
                data += os.read(master, 1024).decode('utf-8')
            except OSError:
                break

        if data != "":
            print(filler + "\r", end="") # Clear previous spinner line
            if end == "\n":
                print("\033[A", end="") # Move up one line
            end = "" if data.endswith("\n") else "\n"
            print(data,end=end)
            print(spinnertext, end="\r")
        else:
            print(spinnertext, end="\r")


    cursor.show()
    spinnertext = h.frame()
    print(filler + "\r") # Clear previous spinner line
    sys.stdout.flush()
    return errbuf


def run_cmd(command: str) -> bool:
    log_cmd(command)
    errbuf = ""
    if config.conf.confirmcmd and not config.conf.dryrun:
        if input("Continue? [y/N]: ").lower() not in 'yY':
            return False

    if config.conf.dryrun:
        return True
    try:
        master, slave = pty.openpty()
        errmaster, errslave = pty.openpty()
        result = subprocess.Popen(command, shell=True, text=True, stdout=slave, stderr=errslave, bufsize=0)
        os.close(slave)
        os.close(errslave)
        flags = fcntl.fcntl(master, fcntl.F_GETFL)
        fcntl.fcntl(master, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        flags = fcntl.fcntl(errmaster, fcntl.F_GETFL)
        fcntl.fcntl(errmaster, fcntl.F_SETFL, flags | os.O_NONBLOCK)

        if sys.stdout.isatty():
            errbuf = status_logs(command, master, errmaster)
        else:
            direct_logs(command, master, errmaster)

        retcode = result.wait()
        if retcode != 0:
            logger.error("Command '%s' failed with code %d", command, retcode)
            if errbuf:
                logger.error("stderr:\n")
                print(errbuf)
        return retcode == 0

    except subprocess.CalledProcessError as e:
        logger.error("Command '%s' failed with error: %d", command, e.returncode)
        return False

def spawn_editor(command) -> int:
    cmdstr = command if isinstance(command, str) else " ".join(command)
    log_cmd(cmdstr)
    if config.conf.dryrun:
        return 0
    result = subprocess.run(command, shell=isinstance(command, str),
                            stdin=None, stdout=None, stderr=None)
    return result.returncode

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

def get_zip_cmd():
    cmd = "gzip"
    if shutil.which("pigz") is not None:
        cmd = "pigz"

    return cmd + f" -{config.conf.complevel}"
