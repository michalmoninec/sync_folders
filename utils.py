import shutil
from pathlib import Path

def create_file(src: Path, dst: Path) -> None:
    shutil.copy(src, dst)

def remove_file(dst: Path) -> None:
    Path.unlink(dst)

def update_file(src: Path, dst: Path) -> None:
    Path.unlink(dst)
    shutil.copy(src, dst)

def create_dir(dst: Path) -> None:
    dst.mkdir(parents=True)

def remove_dir(dst: Path) -> None:
    dst.rmdir()