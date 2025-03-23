# HighHeat

If you are in a hurry, baking with HighHeat is the way to go.

HighHeat is an alternative to bitbake for fast iterative development. To reduce the time from changing the code to running it on the target, HighHeat skips the whole bitbake process and builds the recipe directly in the workdir and deploys it to the existing image on the target.
HighHeat is compatible with [Moulin](https://github.com/xen-troops/moulin)

# Roadmap
- [x] Implement edit
- [x] Implement build
- [x] Implement deploy
- [x] Implement project autodetection
- [x] Implement confirmation before running any shell commands
- [x] Add support for ramdisk images
- [x] Add support for remote targets
- [ ] Add support for non-standard projects (xen, linux)
- [ ] Make non-standard projects moulin-aware(?)
- [ ] Advanced deploy target (subfolders inside images)
- [ ] Option to do remote via sshfs

# Installation
Symlink main.py to somewhere in your PATH, and make it executable.
~~~bash
ln -s /path/to/highheat/main.py /usr/local/bin/hh
chmod +x /usr/local/bin/hh
~~~

# Usage
~~~
usage: hh [-h] [--verbose] [--dryrun] [--noconfirm] {edit,e,build,b,deploy,d,build-deploy,bd} ...

HighHeat, a fast BitBake alternative

positional arguments:
  {edit,e,build,b,deploy,d,build-deploy,bd}
                        Action to perform
    edit (e)            Open source dir in editor
    build (b)           Build project
    deploy (d)          Deploy project
    build-deploy (bd)   Build and deploy the project

options:
  -h, --help            show this help message and exit
  --verbose, -v         Verbose output
  --dryrun, -n          Dry run
  --noconfirm, -y       Do not confirm commands

Examples:

    Edit xen from DomD:
        hh edit domd xen

    Build xen-tools current yocto project:
        hh build xen-tools

    Deploy xen-tools to /srv/tftp:
        hh deploy xen-tools somehost:/srv/tftp

    Deploy qemu to domd-rootfs.ext4:
        hh deploy qemu /path/to/domd-rootfs.ext
~~~

The three main actions are edit, build and deploy.
Edit opens the project source in the preferred editor.
Build builds the project (runs the do_compile/install/deploy scripts).
Deploy copies the built project to the target.

Each command accepts the domain in the project name as an argument. Domain is only relevant for [Moulin](https://github.com/xen-troops/moulin) projects with multiple domains.
For HH to be able to find the correct project, you need to run it from somewhere inside the yocto or moulin root directory.

Targets for deploy:
* Local/remote directory
* Local/remote ext4 image
* Local/remote initrd image

# Configuration
HighHeat searches for the configuration file in the following order:
~~~bash
$XDG_CONFIG_HOME/.config/highheat.yaml
$HOME/.config/highheat.yaml
./highheat.yaml
~~~

Sample configuration:
~~~yaml
editor: nvim # Preferred editor
confirm: true # Confirm before running shell commands
dl_dir: /path/to/downloads # Persistent downloads directory
~~~
