import pytest


from pathlib import Path
from src.main import (
    sync_folders,
    get_parser,
    validate_args,
    files_have_same_hash,
)


def test_failed():
    """Random update"""
    pass


def test_new_dir(new_temp_dir, empty_playground):
    """
    Test that a new directory is created in the replica directory.

    Args:
        new_temp_dir (Path): The new temporary directory to be created.
        empty_playground (dict): Dictionary containing source and replica directories.
    """
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert new_temp_dir.exists()


def test_new_file(new_temp_file, empty_playground):
    """
    Test that a new file is created in the replica directory.

    Args:
        new_temp_file (Path): The new temporary file to be created.
        empty_playground (dict): Dictionary containing source and replica directories.
    """
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert new_temp_file.exists()


def test_spare_file(spare_temp_file, empty_playground):
    """
    Test that a spare file is removed from the replica directory.

    Args:
        spare_temp_file (Path): The spare temporary file to be removed.
        empty_playground (dict): Dictionary containing source and replica directories.
    """
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert not spare_temp_file.exists()


def test_spare_dir(spare_temp_dir, empty_playground):
    """
    Test that a spare directory is removed from the replica directory.

    Args:
        spare_temp_dir (Path): The spare temporary directory to be removed.
        empty_playground (dict): Dictionary containing source and replica directories.
    """
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    assert not spare_temp_dir.exists()


def test_changed_file(different_file, empty_playground):
    """
    Test that a changed file is updated in the replica directory.

    Args:
        different_file (dict): Dictionary containing the original and changed files.
        empty_playground (dict): Dictionary containing source and replica directories.
    """
    sync_folders(empty_playground["src"], empty_playground["rep"], None)
    fl1 = different_file["fl1"]
    fl2 = different_file["fl2"]
    assert files_have_same_hash(fl1, fl2, chunk_size=1024)


def test_argparser_raised_exceptions(empty_playground):
    """
    Test that the argument parser raises exceptions for invalid arguments.

    Args:
        empty_playground (dict): Dictionary containing source, replica, and log directories.
    """
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
    """
    Test that the argument parser correctly parses valid arguments.

    Args:
        empty_playground (dict): Dictionary containing source, replica, and log directories.
    """
    src = str(empty_playground["src"])
    rep = str(empty_playground["rep"])
    log = str(empty_playground["log"])
    parser = get_parser()
    interval = 5
    chunk_size = 2048

    args = parser.parse_args([src, rep, log, str(interval), str(chunk_size)])
    print(f"path: {args.src_root_path}")
    print(f"src path: {src}")
    assert (
        args.src_root_path == empty_playground["src"]
        and args.rep_root_path == empty_playground["rep"]
        and args.log_dir_path == empty_playground["log"]
        and args.chunk_size == chunk_size
    )
