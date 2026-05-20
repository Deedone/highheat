from highheat.image_uimage import ImageUImage
from highheat import config

from pathlib import Path

import shutil
import pytest


IMAGE_INITIAL = Path("./tests/images/uInitramfs.initial")
IMAGE_INITIAL_UNPACKED = Path("./tests/images/uInitramfs.initial.unpacked")
IMAGE_DEPLOY = Path("./tests/images/uInitramfs.installed_deploy")
IMAGE_DEPLOY_UNPACKED = Path("./tests/images/uInitramfs.installed_deploy.unpacked")
IMAGE_FILES = Path("./tests/images/uInitramfs.installed_filesfiles")
IMAGE_FILES_UNPACKED = Path("./tests/images/uInitramfs.installed_files.unpacked")

@pytest.fixture(autouse = True)
def no_confirm():
    config.conf.confirmcmd = False

def assert_dirs_equal(a: Path, b: Path):

    a_files = [p.relative_to(a) for p in a.rglob("*")]
    b_files = [p.relative_to(b) for p in b.rglob("*")]

    print(a_files)
    print(b_files)

    assert a_files == b_files, f"Directories have different files: {set(a_files) ^ set(b_files)}"

    for file in a_files:
        assert (a / file).is_file() == (b / file).is_file(), f"File type mismatch for {file}"
        if (a / file).is_file():    
            assert (a / file).read_bytes() == (b / file).read_bytes(), f"File content mismatch for {file}"

def test_mount_unmount(tmp_path):
    inp = tmp_path / "uInitramfs" 
    shutil.copy(IMAGE_INITIAL, inp)

    img = ImageUImage(inp)

    mounted = img.mount()

    assert mounted is not None
    assert_dirs_equal(mounted, IMAGE_INITIAL_UNPACKED)


    ret = img.umount()
    assert ret == True, "Failed to umount image"


    # Mount again to check that the image is still valid after umount
    mounted = img.mount()
    assert mounted is not None
    assert_dirs_equal(mounted, IMAGE_INITIAL_UNPACKED)


def test_install_files(tmp_path):
    inp = tmp_path / "uInitramfs" 
    shutil.copy(IMAGE_INITIAL, inp)

    img = ImageUImage(inp)

    mounted = img.mount()

    assert mounted is not None
    assert_dirs_equal(mounted, IMAGE_INITIAL_UNPACKED)

    assert img.install(Path("./tests/images/sample_project/image/"), mounted)

    img.umount()

    mounted = img.mount()
    assert mounted is not None

    assert_dirs_equal(mounted, IMAGE_FILES_UNPACKED)

def test_install_deploy(tmp_path):
    inp = tmp_path / "uInitramfs" 
    shutil.copy(IMAGE_INITIAL, inp)

    img = ImageUImage(inp)

    mounted = img.mount()

    assert mounted is not None
    assert_dirs_equal(mounted, IMAGE_INITIAL_UNPACKED)

    assert img.install(Path("./tests/images/sample_project/deploy/Image"), mounted / "test_file")

    img.umount()

    mounted = img.mount()
    assert mounted is not None

    assert_dirs_equal(mounted, IMAGE_DEPLOY_UNPACKED)
