from log import logger
from pathlib import Path


def find_yocto_root() -> Path | None:
    start = Path.cwd()
    while start != Path('/'):
        localconf = start / "conf" / "local.conf"
        if localconf.exists():
            return start
        start = start.parent

    logger.error("yocto root not found")
    return None

def get_project_workdir(builddir: Path, project: str) -> Path | None:
    workdir = builddir / "tmp/work"
    if not workdir.exists():
        logger.error("workdir %s does not exist", workdir)
        return None

    for subdir in workdir.iterdir():
        if subdir.is_dir():
            for subsubdir in subdir.iterdir():
                if subsubdir.is_dir() and subsubdir.name == project:
                    return list(subsubdir.glob("*"))[0]
    return None

def get_project_srcdir(builddir: Path, project: str) -> Path | None:
    base = get_project_workdir(builddir, project)
    if base is None:
        return None

    gitdir = base / "git"
    if not gitdir.exists():
        logger.error("gitdir %s does not exist", gitdir)
        return None

    return gitdir
