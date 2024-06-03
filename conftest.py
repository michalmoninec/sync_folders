from main import sync_folders
from pathlib import Path
from pytest import fixture
import shutil
import tempfile

@fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname

@fixture
def empty_playground(temp_dir):
    print(temp_dir)
    src = Path(temp_dir + "/src")
    src.mkdir()
    rep = Path(temp_dir + "/rep")
    rep.mkdir()
    log = Path(temp_dir + "/log")
    log.mkdir()
    
    try:
        yield [src, rep, log]
    finally:
        shutil.rmtree(src)
        shutil.rmtree(rep)
        shutil.rmtree(log)


@fixture
def new_temp_dir(empty_playground):
    src = empty_playground[0]
    rep = empty_playground[1]

    temp_dir = src / "new_dir"
    temp_dir.mkdir()
    sync_folders(src, rep)
    try:
        yield rep / "new_dir"
    finally:
        temp_dir.rmdir()

@fixture
def new_temp_file(empty_playground):
    src = empty_playground[0]
    rep = empty_playground[1]

    temp_dir = src / "new_file.txt"
    temp_dir.touch()
    sync_folders(src, rep)
    try:
        yield rep / "new_file.txt"
    finally:
        temp_dir.unlink()

@fixture
def spare_temp_file(empty_playground):
    src = empty_playground[0]
    rep = empty_playground[1]

    temp_dir = rep / "new_file.txt"
    temp_dir.touch()
    sync_folders(src, rep)
    try:
        yield rep / "new_file.txt"
    finally:
        if temp_dir.exists():
            temp_dir.unlink()

@fixture
def spare_temp_dir(empty_playground):
    src = empty_playground[0]
    rep = empty_playground[1]

    temp_dir = rep / "new_dir"
    temp_dir.mkdir()
    sync_folders(src, rep)
    try:
        yield rep / "new_dir"
    finally:
        if temp_dir.exists():
            temp_dir.rmdir()

@fixture
def different_file(empty_playground):
    src = empty_playground[0]
    rep = empty_playground[1]

    fl1 = src / "new_file.txt"
    fl1.touch()
    fl1.write_text("Hello, there.")
    fl2 = rep / "new_file.txt"
    fl2.touch()
    fl2.write_text("General, Kenobi")

    sync_folders(src, rep)
    try:
        yield [fl1, fl2]
    finally:
        shutil.copy(fl1, fl2)