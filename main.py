#!/usr/bin/env python3
import argparse
import moulin
import yocto
import config
import sys
from log import logger, set_debug
from pathlib import Path
from project import find_project
import time


def get_yoctobuilddir(domain:str|None) -> Path | None:
    if domain:
        yaml_path = moulin.find_yaml_path()
        logger.debug("yaml_path %s", yaml_path)

        if not yaml_path:
            return None

        build_dirs = moulin.get_build_dirs(yaml_path)
        if domain not in build_dirs:
            logger.error("domain %s not found in %s", domain, build_dirs)
            return None

        return build_dirs[domain]
    else:
        builddir = yocto.find_yocto_root()
        return builddir


def guess_project() -> str | None:
    cwd = Path.cwd()

    while cwd != Path('/'):
        if (cwd / 'temp/run.do_compile').exists():
            return cwd.parent.name
        cwd = cwd.parent

    return None


def process_args() -> argparse.Namespace:
    epilog = """Examples:

    If target is an image, you can specify additional subpath to be used
    inside the unpacked image.
    Example:
        hh deploy linux host:/tftpdir/uInitrams,/path/to/linux

    Edit xen from DomD:
        hh edit domd xen

    Build xen-tools current yocto project:
        hh build xen-tools

    Deploy xen-tools to /srv/tftp:
        hh deploy xen-tools somehost:/srv/tftp

    Deploy qemu to domd-rootfs.ext4:
        hh deploy qemu /path/to/domd-rootfs.ext

"""

    parser = argparse.ArgumentParser(description='HighHeat, a fast BitBake alternative', epilog=epilog, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--verbose', '-v', default=False, action="store_true", help='Verbose output')
    parser.add_argument('--dryrun', '-n', default=False, action="store_true", help='Dry run')
    parser.add_argument('--noconfirm', '-y', default=False, action="store_true", help='Do not confirm commands')

    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    parser_edit = subparsers.add_parser('edit', help='Open source dir in editor', aliases=['e'])
    parser_edit.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_edit.add_argument('project', type=str, help='Project name, e.g. "linux"')

    parser_build = subparsers.add_parser('build', help='Build project', aliases=['b'])
    parser_build.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_build.add_argument('project', type=str, nargs="?", help='Project name, e.g. "linux"')

    parser_deploy = subparsers.add_parser('deploy', help='Deploy project', aliases=['d'])
    parser_deploy.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_deploy.add_argument('project', type=str, nargs="?", help='Project name, e.g. "linux"')
    parser_deploy.add_argument('target', type=str, help='Target: path do folder, image')

    parser_deploy = subparsers.add_parser('build-deploy', help='Build and deploy the project', aliases=['bd'])
    parser_deploy.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_deploy.add_argument('project', type=str, nargs="?", help='Project name, e.g. "linux"')
    parser_deploy.add_argument('target', type=str, help='Target: path do folder, image')

    args = parser.parse_args()
    if not args.action:
        parser.print_help()
        sys.exit(1)

    return args


def main():
    conf = config.load()
    start = time.time()
    args = process_args()

    if args.verbose:
        conf.verbose = True
        set_debug()

    logger.debug(args)
    logger.debug(conf)

    if args.dryrun:
        conf.dryrun = True

    if args.noconfirm:
        conf.confirmcmd = False

    if args.domain and not args.project:
        args.project = args.domain
        args.domain = None
        logger.debug("New args %s", args)

    if not args.project:
        args.project = guess_project()
        if not args.project:
            logger.error("Project not found")
            return
        else:
            logger.info("Detected project %s", args.project)


    yoctobuilddir = get_yoctobuilddir(args.domain)
    if not yoctobuilddir:
        logger.error("Yocto build dir not found")
        return

    logger.debug("Yocto build dir %s", yoctobuilddir)

    proj = find_project(yoctobuilddir, args.project)
    if not proj or not proj.initialized:
        logger.error("Project %s not found", args.project)
        return

    if args.action == "edit" or args.action == "e":
        proj.edit()
    elif args.action == "build" or args.action == "b":
        proj.build()
    elif args.action == "deploy" or args.action == "d":
        proj.deploy(args.target)
    elif args.action == "build-deploy" or args.action == "bd":
        ret = proj.build()
        if not ret:
            return
        proj.deploy(args.target)

    elapsed_time = time.time() - start
    formatted_time = time.strftime("%H:%M:%S", time.gmtime(elapsed_time))
    logger.info("Execution took: %s", formatted_time)

main()
