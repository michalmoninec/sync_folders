"""
This module contains pytest fixtures for setting up and tearing down
temporary directories and files for testing the sync_folders functionality.
"""

from pathlib import Path
from pytest import fixture
import shutil
import tempfile


@fixture
def temp_dir():
    """
    Fixture to create a temporary directory.

    Yields:
        str: The path to the temporary directory.
    """
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


@fixture
def empty_playground(temp_dir):
    """
    Fixture to set up an empty playground with source, replica, and log directories.

    Args:
        temp_dir (str): The path to the temporary directory.

    Yields:
        dict: A dictionary containing paths to the source, replica, and log directories.
    """
    src = Path(temp_dir) / "src"
    src.mkdir()
    rep = Path(temp_dir) / "rep"
    rep.mkdir()
    log = Path(temp_dir) / "log"
    log.mkdir()
    data = {"src": src, "rep": rep, "log": log}
    try:
        yield data
    finally:
        shutil.rmtree(src)
        shutil.rmtree(rep)
        shutil.rmtree(log)


@fixture
def new_temp_dir(empty_playground):
    """
    Fixture to create a new temporary directory in the source directory.

    Args:
        empty_playground (dict): A dictionary containing paths to the source, replica, and log directories.

    Yields:
        Path: The path to the new temporary directory in the replica directory.
    """
    src = empty_playground["src"]
    rep = empty_playground["rep"]

    temp_dir = src / "new_dir"
    temp_dir.mkdir()

    try:
        yield rep / "new_dir"
    finally:
        temp_dir.rmdir()


@fixture
def new_temp_file(empty_playground):
    """
    Fixture to create a new temporary file in the source directory.

    Args:
        empty_playground (dict): A dictionary containing paths to the source, replica, and log directories.

    Yields:
        Path: The path to the new temporary file in the replica directory.
    """
    src = empty_playground["src"]
    rep = empty_playground["rep"]

    temp_file = src / "new_file.txt"
    temp_file.touch()

    try:
        yield rep / "new_file.txt"
    finally:
        temp_file.unlink()


@fixture
def spare_temp_file(empty_playground):
    """
    Fixture to create a spare temporary file in the replica directory.

    Args:
        empty_playground (dict): A dictionary containing paths to the source, replica, and log directories.

    Yields:
        Path: The path to the spare temporary file in the replica directory.
    """
    rep = empty_playground["rep"]

    temp_file = rep / "new_file.txt"
    temp_file.touch()

    try:
        yield temp_file
    finally:
        temp_file.unlink()


@fixture
def spare_temp_dir(empty_playground):
    """
    Fixture to create a spare temporary directory in the replica directory.

    Args:
        empty_playground (dict): A dictionary containing paths to the source, replica, and log directories.

    Yields:
        Path: The path to the spare temporary directory in the replica directory.
    """
    rep = empty_playground["rep"]

    temp_dir = rep / "spare_dir"
    temp_dir.mkdir()

    try:
        yield temp_dir
    finally:
        temp_dir.rmdir()


@fixture
def different_file(empty_playground):
    src = empty_playground["src"]
    rep = empty_playground["rep"]

    fl1 = src / "new_file.txt"
    fl1.touch()
    fl1.write_text("Hello, there.")
    fl2 = rep / "new_file.txt"
    fl2.touch()
    fl2.write_text("General, Kenobi")
    data = {"fl1": fl1, "fl2": fl2}
    try:
        yield data
    finally:
        shutil.copy(fl1, fl2)
