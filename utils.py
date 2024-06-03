import shutil
import logging
from pathlib import Path

def logging_handle(prefix: str, suffix: int) -> None:
    def logging_outer(func):
        def wrapper(*args, **kwargs):
            logging.info(f"{prefix}: {args[suffix]}")
            return func(*args, **kwargs)
        return wrapper
    return logging_outer

@logging_handle('CREATED FILE', 1)
def create_file(src: Path, dst: Path) -> None:
    shutil.copy(src, dst)

@logging_handle('REMOVED FILE', 0)
def remove_file(dst: Path) -> None:
    Path.unlink(dst)

@logging_handle('UPDATED FILE', 1)
def update_file(src: Path, dst: Path) -> None:
    Path.unlink(dst)
    shutil.copy(src, dst)

@logging_handle('CREATED DIR', 0)
def create_dir(dst: Path) -> None:
    dst.mkdir(parents=False, exist_ok=True)

@logging_handle('REMOVED DIR', 0)
def remove_dir(dst: Path) -> None:
    dst.rmdir()