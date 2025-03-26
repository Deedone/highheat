# HighHeat

If you are in a hurry, baking with HighHeat is the way to go.

HighHeat offers a swift alternative to BitBake for rapid iterative development. By bypassing the entire BitBake process, HighHeat directly builds the recipe in the work directory and deploys it to the existing image on the target, significantly reducing the time from code changes to execution. Additionally, HighHeat is compatible with [Moulin](https://github.com/xen-troops/moulin).

HH does not check any dependencies, nor does it create images from scratch or touches bitbake metadata. You need to have the project built at least once with BitBake before using HighHeat.

# Roadmap
- [x] Implement edit
- [x] Implement build
- [x] Implement deploy
- [x] Implement project autodetection
- [x] Implement confirmation before running any shell commands
- [x] Add support for ramdisk images
- [x] Add support for remote targets
- [ ] Add support for non-standard projects (xen, linux)
- [ ] Try to get rid of sudo
- [ ] Make non-standard projects moulin-aware(?)
- [x] Advanced deploy targets (subfolders inside images)
- [ ] Option to do remote via sshfs
- [ ] Compile commands generation
- [ ] Local image editing

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
~~~

The three main actions are edit, build and deploy.
Edit opens the project source in the preferred editor.
Build builds the project (runs the do_compile/install/deploy scripts).
Deploy copies the built project to the target.

Each command accepts the domain and the project name as arguments. Domain is only relevant for [Moulin](https://github.com/xen-troops/moulin) projects with multiple domains.
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
