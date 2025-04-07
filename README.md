# HighHeat

If you are in a hurry, baking with HighHeat is the way to go.

HighHeat offers a fast alternative to BitBake for rapid iterative development. By bypassing the entire BitBake process, HighHeat directly builds the recipe in the work directory and deploys it to the existing image on the target, significantly reducing the time from code changes to execution. Additionally, HighHeat is compatible with [Moulin](https://github.com/xen-troops/moulin).

HH does not check any dependencies, nor does it create images from scratch or touches bitbake metadata. You need to have the project built at least once with BitBake before using HighHeat.

# Reasoning (rambling)

Yocto is a very good tool, until you start developing with it. (c) padre

My main problem with developing inside Yocto is that there is no good way to iterate on your changes. You basically have two options:
You can either rebuild everything with bitbake, which takes an ungodly amount of time, or dive inside the "guts" of the workdir and try to do something faster by hand, which is very tedious and breaks you out of the development loop.

For some time I managed to work around this by using a lot of bash scripts, but
this approach is not very reliable or pleasant.

So the time has come to create a better solution. Now, instead of finding the relevant workdir, running "compile, install, deploy" loop, downloading the relevant image from the target, unpacking/mounting it by hand, finding and copying the relevant files, and packing and uploading everything back to the target, you can just do this:

`hh build-deploy project-name target-path`

And HH will do all of that for you.

# Roadmap
- [x] Implement edit
- [x] Implement build
- [x] Implement deploy
- [x] Implement project autodetection
- [x] Implement confirmation before running any shell commands
- [x] Add support for ramdisk images
- [x] Add support for remote targets
- [x] Add support for non-standard projects (xen, linux)
- [x] Try to get rid of sudo
- [x] Advanced deploy targets (subfolders inside images)
- [ ] Option to do remote via sshfs
- [ ] Compile commands generation
- [ ] Local image editing

# Installation
Install with `pip`

~~~bash
pip3 install --user git+https://github.com/deedone/highheat
~~~

# Usage
~~~bash
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

If target is an image, you can specify additional subpath to be used
inside the unpacked image.
Example:
    hh deploy linux host:/tftpdir/uInitrams,/path/to/linux

Linux project handles both Kernel image and DTB files, depending on target path.
Example:
    hh deploy linux host:/tftpdir/uInitrams,/path/to/linux
    hh deploy linux host:/tftpdir/uInitrams,/path/to/file.dtb

Other examples:

    Edit xen from DomD:
        hh edit domd xen

    Build xen-tools current yocto project:
        hh build xen-tools
        
    Autodetect and build the project (based on the current directory)
        hh build

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
editor: vim # Preferred editor
confirm: True # Confirm before running shell commands
dl_dir: ~/.cache/highheat # Persistent downloads directory
dldir_cleanup_interval: 7 # Days between cleanup of old downloads
~~~
