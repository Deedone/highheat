from log import logger
from pathlib import Path
import time


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


def get_project_gitdir(builddir: Path, project: str) -> Path | None:
    base = get_project_workdir(builddir, project)
    if base is None:
        return None

    gitdir = base / "git"
    if not gitdir.exists():
        return None

    return gitdir


def get_project_nongit_srcdir(builddir: Path, project: str) -> Path | None:
    base = get_project_workdir(builddir, project)
    if base is None:
        return None

    candidates = list(base.glob(project + "-*"))
    candidates = list(filter(lambda x: x.is_dir(), candidates))
    if len(candidates) < 1:
        logger.error("No source candidate found for %s", project)
        return None
    if len(candidates) > 1:
        logger.warn("Multiple source dir candidates found for %s", project)
        logger.warn("%s", [x.name for x in candidates])
        logger.warn("Using the first one %s", candidates[0].name)
        time.sleep(5)
    return candidates[0]


def get_kernel_srcdir(builddir: Path) -> Path|None:
    work_shared = builddir / "tmp/work-shared"
    if not work_shared.exists():
        logger.error("Work-shared doesn't exist")
        return None

    for subdir in work_shared.iterdir():
        kernel_source = subdir / "kernel-source"
        if kernel_source.exists():
            return kernel_source

    return None
