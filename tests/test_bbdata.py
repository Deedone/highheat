import json

import pytest

from highheat.bbdata import BBdata, ProjectData, CURRENT_VERSION


@pytest.fixture
def sample_project():
    return ProjectData(
        sourcedir="/work/src",
        imagedir="/work/image",
        deploydir="/work/deploy",
        workdir="/work",
        recpie_path="/layers/meta-foo/recipes-core/foo.bb",
        srcrev="abc123",
        recipes=["/layers/meta-foo/recipes-core/foo.bb",
                 "/layers/meta-bar/recipes-core/foo.bbappend"],
    )


def test_save_creates_file(tmp_path, sample_project):
    bb = BBdata(tmp_path)
    bb.append("foo", sample_project)

    assert (tmp_path / ".hh_data.json").exists()


def test_save_writes_current_version(tmp_path, sample_project):
    bb = BBdata(tmp_path)
    bb.append("foo", sample_project)

    raw = json.loads((tmp_path / ".hh_data.json").read_text())
    assert raw["version"] == str(CURRENT_VERSION)
    assert "foo" in raw


def test_roundtrip_preserves_fields(tmp_path, sample_project):
    bb = BBdata(tmp_path)
    bb.append("foo", sample_project)

    reloaded = BBdata(tmp_path)
    assert "foo" in reloaded.data
    got = reloaded.data["foo"]
    assert got.sourcedir == sample_project.sourcedir
    assert got.imagedir == sample_project.imagedir
    assert got.deploydir == sample_project.deploydir
    assert got.workdir == sample_project.workdir
    assert got.recpie_path == sample_project.recpie_path
    assert got.srcrev == sample_project.srcrev
    assert got.recipes == sample_project.recipes


def test_load_missing_file_yields_empty(tmp_path):
    bb = BBdata(tmp_path)
    assert bb.data == {}


def test_load_corrupt_json_yields_empty(tmp_path):
    (tmp_path / ".hh_data.json").write_text("{not valid json")
    bb = BBdata(tmp_path)
    assert bb.data == {}


def test_load_version_mismatch_yields_empty(tmp_path, sample_project):
    bb = BBdata(tmp_path)
    bb.append("foo", sample_project)

    raw = json.loads((tmp_path / ".hh_data.json").read_text())
    raw["version"] = "999"
    (tmp_path / ".hh_data.json").write_text(json.dumps(raw))

    reloaded = BBdata(tmp_path)
    assert reloaded.data == {}


def test_multiple_projects_roundtrip(tmp_path, sample_project):
    other = ProjectData(
        sourcedir="/work/src2",
        imagedir=None,
        deploydir=None,
        workdir="/work2",
        recpie_path="/layers/meta-foo/recipes-core/bar.bb",
        srcrev="def456",
        recipes=["/layers/meta-foo/recipes-core/bar.bb"],
    )
    bb = BBdata(tmp_path)
    bb.append("foo", sample_project)
    bb.append("bar", other)

    reloaded = BBdata(tmp_path)
    assert set(reloaded.data.keys()) == {"foo", "bar"}
    assert reloaded.data["bar"].imagedir is None
    assert reloaded.data["bar"].deploydir is None


def test_append_persists_immediately(tmp_path, sample_project):
    bb = BBdata(tmp_path)
    bb.append("foo", sample_project)

    raw = json.loads((tmp_path / ".hh_data.json").read_text())
    assert "foo" in raw
