from log import logger
from pathlib import Path
from bbdata import BBdata

def find_yocto_root(start: Path) -> Path | None:
    while start != Path('/'):
        localconf = start / "conf" / "local.conf"
        if localconf.exists():
            return start
        start = start.parent

    logger.error("yocto root not found")
    return None
    
    
def find_yocto_source(start: Path) -> Path | None:
    while start != Path('/'):
        poky_path = start / "poky"
        if poky_path.exists():
            return start
        start = start.parent

    logger.error("yocto source not found")
    return None
    

def _load_bbdata(builddir: Path, project: str) -> BBdata | None:
    bbdata = BBdata(builddir)
    yocto_root = find_yocto_source(builddir)
    if not yocto_root:
        return None
    
    if not bbdata.check_entry(project):
        if not bbdata.bb_load_projectdata(yocto_root, builddir, project):
            logger.error("failed to load project data for %s", project)
            return None
        
    return bbdata


def get_project_workdir(builddir: Path, project: str) -> Path | None:
    bbdata = _load_bbdata(builddir, project)
    if not bbdata:
        return None
        
    return bbdata.data[project].workdir


def get_project_srcdir(builddir: Path, project: str) -> Path | None:
    bbdata = _load_bbdata(builddir, project)
    if not bbdata:
        return None
        
    return bbdata.data[project].sourcedir
    
    
def get_project_imagedir(builddir: Path, project: str) -> Path | None:
    bbdata = _load_bbdata(builddir, project)
    if not bbdata:
        return None
            
    return bbdata.data[project].imagedir


def get_project_deploydir(builddir: Path, project: str) -> Path | None:
    bbdata = _load_bbdata(builddir, project)
    if not bbdata:
        return None
            
    return bbdata.data[project].deploydir
