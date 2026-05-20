import pytest

from highheat.yocto import find_yocto_build_dir, find_yocto_source


@pytest.fixture
def yocto_tree(tmp_path):
    build = tmp_path / "build"
    (build / "conf").mkdir(parents=True)
    (build / "conf" / "local.conf").write_text("MACHINE = 'qemux86-64'\n")
    (build / "tmp" / "work" / "core-image").mkdir(parents=True)
    (tmp_path / "poky").mkdir(parents=True)
    return tmp_path


@pytest.fixture
def yocto_tree_build(yocto_tree):
    return yocto_tree / "build"


def test_finds_root_from_nested_dir(yocto_tree_build):
    nested = yocto_tree_build / "build" / "tmp" / "work" / "core-image"
    assert find_yocto_build_dir(nested) == yocto_tree_build


def test_returns_none_when_no_local_conf(tmp_path):
    (tmp_path / "some" / "dir").mkdir(parents=True)
    assert find_yocto_build_dir(tmp_path / "some" / "dir") is None


def test_picks_innermost_root_when_nested(tmp_path):
    outer = tmp_path / "outer"
    inner = outer / "sub" / "inner"
    (outer / "conf").mkdir(parents=True)
    (outer / "conf" / "local.conf").write_text("")
    (inner / "conf").mkdir(parents=True)
    (inner / "conf" / "local.conf").write_text("")

    deep = inner / "tmp"
    deep.mkdir()
    assert find_yocto_build_dir(deep) == inner


@pytest.mark.parametrize("start_subdir", ["", "tmp", "tmp/work", "tmp/work/core-image"])
def test_finds_root_from_various_depths(yocto_tree_build, start_subdir):
    start = yocto_tree_build / start_subdir if start_subdir else yocto_tree_build
    assert find_yocto_build_dir(start) == yocto_tree_build 


@pytest.mark.parametrize("start_subdir", ["", "tmp", "tmp/work", "tmp/work/core-image"])
def test_finds_source_from_various_depths(yocto_tree, start_subdir):
    start = yocto_tree / start_subdir if start_subdir else yocto_tree
    assert find_yocto_source(start) == yocto_tree 
