# HighHeat

If you are in a hurry, baking with HighHeat is the way to go.

HighHeat is an alternative to bitbake for fast iterative development. To reduce the time from changing the code to running it on the target, HighHeat skips the whole bitbake process and builds the recipe directly in the workdir and deploys it to the existing image on the target.
HighHeat is compatible with [Moulin](https://github.com/xen-troops/moulin)

# Roadmap
- [x] Implement edit
- [x] Implement build
- [x] Implement deploy
- [ ] Implement project autodetection
- [ ] Implement confirmation before running any shell commands
- [ ] Add support for ramdisk images
- [ ] Add support for remote targets
- [ ] Add support for non-standard projects (xen, linux)
- [ ] Make non-standard projects moulin-aware
- [ ] Advanced deploy target (subfolders inside images)

# Installation
Symlink main.py somewhere in your PATH, for example:
~~~
ln -s /path/to/highheat/main.py /usr/local/bin/hh
~~~

# Usage
~~~
usage: hh [-h] [--verbose] [--dryrun] {edit,build,deploy} ...

HighHeat, a fast BitBake alternative

positional arguments:
  {edit,build,deploy}  Action to perform
    edit               Open source dir in editor
    build              Build project
    deploy             Deploy project

options:
  -h, --help           show this help message and exit
  --verbose, -v        Verbose output
  --dryrun, -n         Dry run

Examples:

    Edit xen from DomD:
        hh edit domd xen

    Build xen-tools in current yocto project:
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
