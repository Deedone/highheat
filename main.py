#!/usr/bin/env python3
import argparse
import moulin
import yocto
import config
from log import logger
from pathlib import Path
from project import find_project


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


def main():
    conf = config.load()

    epilog = """Examples:

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

    subparsers = parser.add_subparsers(dest='action', help='Action to perform')

    parser_edit = subparsers.add_parser('edit', help='Open source dir in editor')
    parser_edit.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_edit.add_argument('project', type=str, help='Project name, e.g. "linux"')

    parser_build = subparsers.add_parser('build', help='Build project')
    parser_build.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_build.add_argument('project', type=str, nargs="?", help='Project name, e.g. "linux"')

    parser_deploy = subparsers.add_parser('deploy', help='Deploy project')
    parser_deploy.add_argument('domain', type=str, nargs="?", help='Project\'s domain, e.g. "domd"')
    parser_deploy.add_argument('project', type=str, help='Project name, e.g. "linux"')
    parser_deploy.add_argument('target', type=str, help='Target: path do folder, image')

    args = parser.parse_args()

    if not args.action:
        parser.print_help()
        return

    logger.debug(args)
    logger.debug(conf)

    if args.verbose:
        conf.verbose = True

    if args.dryrun:
        conf.dryrun = True

    if args.domain and not args.project:
        args.project = args.domain
        args.domain = None
        logger.debug("New args %s", args)

    yoctobuilddir = get_yoctobuilddir(args.domain)
    if not yoctobuilddir:
        logger.error("Yocto build dir not found")
        return

    logger.debug("Yocto build dir %s", yoctobuilddir)
    proj = find_project(yoctobuilddir, args.project)
    if not proj or not proj.initialized:
        logger.error("Project %s not found", args.project)
        return

    if args.action == "edit":
        proj.edit()
    elif args.action == "build":
        proj.build()
    elif args.action == "deploy":
        proj.deploy(args.target)



main()
