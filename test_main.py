import pytest
import argparse

from pathlib import Path

from main import sync_folders, get_parser, validate_args
from main import files_have_same_hash


def test_new_dir(new_temp_dir, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert new_temp_dir.exists()


def test_new_file(new_temp_file, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert new_temp_file.exists()


def test_spare_file(spare_temp_file, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert not spare_temp_file.exists()


def test_spare_dir(spare_temp_dir, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert not spare_temp_dir.exists()


def test_changed_file(different_file, empty_playground):
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    fl1 = different_file["fl1"]
    fl2 = different_file["fl2"]
    assert files_have_same_hash(fl1, fl2, chunk_size=1024)


def test_argparser_raised_exceptions(empty_playground):
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
        parser.parse_args([src, rep, log, "5", "-1"])

    with pytest.raises(SystemExit):
        validate_args(parser, Path(src), Path(rep), Path(src))

    with pytest.raises(SystemExit):
        validate_args(parser, Path(src), Path(rep), Path(rep))


def test_valid_args(empty_playground):
    src = str(empty_playground["src"])
    rep = str(empty_playground["rep"])
    log = str(empty_playground["log"])
    parser = get_parser()

    args = parser.parse_args([src, rep, log, "5", "2048"])
    assert (
        args.src_root_path == src
        and args.rep_root_path == rep
        and args.log_dir_path == log
        and args.chunk_size == 2048,
    )
