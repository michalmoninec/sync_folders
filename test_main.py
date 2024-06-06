from main import sync_folders, get_parser, validate_args
import argparse
from pathlib import Path
from pytest import fixture
import pytest
import tempfile
import shutil
from main import files_have_same_hash


def test_new_dir(new_temp_dir, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"])
    assert new_temp_dir.exists()


def test_new_file(new_temp_file, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"])
    assert new_temp_file.exists()


def test_spare_file(spare_temp_file, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"])
    assert not spare_temp_file.exists()


def test_spare_dir(spare_temp_dir, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"])
    assert not spare_temp_dir.exists()


def test_changed_file(different_file, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"])
    fl1 = different_file["fl1"]
    fl2 = different_file["fl2"]
    assert files_have_same_hash(fl1, fl2)


def test_argparser(empty_playground):
    src = str(empty_playground["src"])
    rep = str(empty_playground["rep"])
    log = str(empty_playground["log"])

    parser = get_parser()

    with pytest.raises(SystemExit):
        parser.parse_args()

    with pytest.raises(SystemExit):
        parser.parse_args([src + "c", rep, log, "5"])

    with pytest.raises(SystemExit):
        parser.parse_args([src, rep + "c", log, "5"])

    with pytest.raises(SystemExit):
        parser.parse_args([src, rep, log + "c", "5"])

    with pytest.raises(SystemExit):
        parser.parse_args([src, rep, log])

    with pytest.raises(SystemExit):
        parser.parse_args([src, rep, log, "0"])

    with pytest.raises(SystemExit):
        parser.parse_args([src, rep, log, ""])

    with pytest.raises(SystemExit):
        validate_args(parser, Path(src), Path(rep), Path(src))

    with pytest.raises(SystemExit):
        validate_args(parser, Path(src), Path(rep), Path(rep))
