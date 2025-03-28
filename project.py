import yocto
import config
import transport
import image
from log import logger

from pathlib import Path
import shell


#Naming
#/home/x/work/prod_devel/yocto/build-domd/tmp/work/cortexa76-poky-linux/xen/4.20.0+gitAUTOINC+dcbbc89203-r0/git
#            |moulindir       | yoctobuilddir                              |workdir                        |srcdir
#TODO: Move copying to image/transport layers (may help minimize sudo)
#TODO: Find some nice way to handle stuff like xenpolicy

class Project:

    workdir:Path = Path()
    srcdir:Path = Path()
    yoctobuilddir:Path = Path()
    name:str = "Simple userspace"
    projname:str = ""
    initialized:bool = False
    tran:transport.Transport|None = None
    img:image.Image|None = None

    def __init__(self, yoctobuilddir:Path, name:str):
        workdir = self.find_workdir(yoctobuilddir, name)
        if not workdir:
            return

        srcdir = self.find_srcdir(yoctobuilddir, name)
        if not srcdir:
            return

        self.yoctobuilddir = yoctobuilddir
        self.srcdir = srcdir
        self.workdir = workdir
        self.projname = name
        self.initialized = True

        logger.debug("Initialized project %s in %s %s", name, workdir, srcdir)


    def find_workdir(self, yoctobuilddir:Path, name:str) -> Path|None:
        return yocto.get_project_workdir(yoctobuilddir, name)

    def find_srcdir(self, yoctobuilddir:Path, name:str) -> Path|None:
        return yocto.get_project_srcdir(yoctobuilddir, name)

    def find_image(self) -> Path|None:
        return yocto.get_project_imagedir(self.yoctobuilddir, self.projname)
    
    def find_deploydir(self) -> Path|None:
        return yocto.get_project_deploydir(self.yoctobuilddir, self.projname)

    def edit(self) -> None:
        logger.debug("edit %s", self.projname)
        if not self.initialized:
            return

        shell.run_cmd(f"{config.conf.editorpath} {self.srcdir}")


    def run_compile(self, workdir: Path) -> bool:
        buildscript = workdir / "temp" / "run.do_compile"

        if not buildscript.exists():
            logger.error("build script %s does not exist", buildscript)
            return False

        return shell.run_cmd(f"{buildscript}")


    def run_install(self, workdir: Path) -> bool:
        buildscript = workdir / "temp" / "run.do_install"

        if not buildscript.exists():
            logger.error("install script %s does not exist", buildscript)
            return False

        return shell.run_cmd(f"{buildscript}")


    def run_deploy(self, workdir: Path) -> bool:
        buildscript = workdir / "temp" / "run.do_deploy"

        if not buildscript.exists():
            logger.warning("deploy script %s does not exist", buildscript)
            return True

        return shell.run_cmd(f"{buildscript}")


    def build(self) -> bool:
        logger.debug("build %s", self.projname)
        if not self.initialized:
            return False

        if not self.run_compile(self.workdir):
            logger.error("Build failed")
            return False

        if not self.run_install(self.workdir):
            logger.error("Install failed")
            return False

        if not self.run_deploy(self.workdir):
            logger.error("Deploy failed")
            return False

        logger.info("%s: Build successful", self.projname)
        return True


    def check_subtarget(self, target: str) -> tuple[str, str|None]:
        parts = target.split(",", 1)
        if len(parts) != 2:
            return target, None
        actual_target, subpath = parts
        return actual_target, subpath


#TODO: Move subpath handling to images
    def prepare_target(self, target:str) -> Path|None:
        target, subpath = self.check_subtarget(target)
        self.tran = transport.find_transport(target)
        if not self.tran:
            logger.error("Transport not found")
            return None

        downloaded = self.tran.download()
        if not downloaded:
            logger.error("Download failed")
            del self.tran
            return None

        self.img = image.find_image(downloaded)
        if not self.img:
            logger.error("Can't determine image type for %s", downloaded)
            del self.tran
            return None

        mounted = self.img.mount()
        if mounted and subpath:
            if subpath.startswith("/"):
                subpath = subpath[1:]
            logger.info("Using subpath %s", subpath)
            mounted = mounted / subpath

        if not mounted:
            logger.error("Mount failed")
            del self.tran
            del self.img
            return None

        return mounted



    def deploy(self, target:str) -> None:
        logger.debug("deploy %s to %s", self.projname, target)
        if not self.initialized:
            return

        image = self.find_image()
        if not image:
            return

        mounted = self.prepare_target(target)

        if not mounted:
            logger.error("Prepare target failed")
            return

        if image.is_dir():
            ret = shell.run_cmd(f"sudo cp -r {image}/* {mounted}")
        else:
            ret = shell.run_cmd(f"sudo cp {image} {mounted}")

        if not ret:
            logger.error("Copy failed")
            return

        logger.info("%s: Deploy successful", self.projname)

        self.cleanup()

    def cleanup(self):
        if self.img:
            self.img.umount()

        if self.tran:
            self.tran.upload()


    @staticmethod
    def can_handle(_target:str) -> bool:
        return True


import project_linux
import project_xen
PROJECT_TYPES = [
    project_linux.ProjectLinux,
    project_xen.ProjectXen,
    Project,
]


def find_project(yoctobuilddir:Path, name:str) -> Project|None:
    for project_type in PROJECT_TYPES:
        if project_type.can_handle(name):
            logger.info("Using %s project type", project_type.name)
            return project_type(yoctobuilddir, name)
    return None
