from pathlib import Path

import pytest

from highheat.image import Image, find_image, needs_mount
from highheat import image_ext4, image_uimage, image_ramfs_gz, image_dtb


@pytest.mark.parametrize("path,expected_cls", [
    ("test.ext4", image_ext4.ImageExt4),
    ("test.uInitramfs", image_uimage.ImageUImage),
    ("test.cpio.gz", image_ramfs_gz.ImageRamfsGZ),
    ("test.dtb", image_dtb.ImageDtb),
    ("test-dtb", image_dtb.ImageDtb),
    ("random_dir", Image),
])
def test_find_image_returns_correct_type(path, expected_cls):
    img = find_image(Path(path))
    assert img is not None
    assert isinstance(img, expected_cls)
    assert img.name == expected_cls.name


def test_find_image_sets_path():
    p = Path("/some/where/test.ext4")
    img = find_image(p)
    assert img.path == p


@pytest.mark.parametrize("path,expected", [
    ("test.ext4", True),
    ("test.uInitramfs", True),
    ("test.cpio.gz", True),
    ("test.dtb", True),
    ("random_dir", False),
])
def test_needs_mount(path, expected):
    assert needs_mount(path) == expected


def test_base_image_mount_returns_path(tmp_path):
    img = Image(tmp_path)
    assert img.mount() == tmp_path


def test_base_image_umount_is_noop(tmp_path):
    assert Image(tmp_path).umount() is True


def test_base_image_can_handle_anything():
    assert Image.can_handle("anything.xyz") is True
    assert Image.can_handle("") is True


def test_install_file(tmp_path, mocker):
    mock_run = mocker.patch("highheat.image.shell.run_cmd", return_value=True)
    src = tmp_path / "file.bin"
    src.write_bytes(b"x")
    dst = tmp_path / "dest"

    assert Image(tmp_path).install(src, dst) is True
    mock_run.assert_called_once_with(f"cp {src} {dst}")


def test_install_directory(tmp_path, mocker):
    mock_run = mocker.patch("highheat.image.shell.run_cmd", return_value=True)
    src = tmp_path / "srcdir"
    src.mkdir()
    dst = tmp_path / "dest"

    assert Image(tmp_path).install(src, dst) is True
    mock_run.assert_called_once_with(f"cp -r {src}/* {dst}")


def test_install_propagates_failure(tmp_path, mocker):
    mocker.patch("highheat.image.shell.run_cmd", return_value=False)
    src = tmp_path / "file.bin"
    src.write_bytes(b"x")

    assert Image(tmp_path).install(src, tmp_path / "dst") is False
