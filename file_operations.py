import shutil
import logging
from pathlib import Path


def log_error(func) -> None:
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(str(e))

    return wrapper


@log_error
def create_file(src: Path, dst: Path) -> None:
    logging.info(f"CREATED FILE: {dst}")
    shutil.copy(src, dst)


@log_error
def remove_file(dst: Path) -> None:
    logging.info(f"REMOVED FILE: {dst}")
    Path.unlink(dst)


@log_error
def update_file(src: Path, dst: Path) -> None:
    logging.info(f"UPDATED FILE> {dst}")
    Path.unlink(dst)
    shutil.copy(src, dst)


@log_error
def create_dir(dst: Path) -> None:
    logging.info(f"CREATED DIR: {dst}")
    dst.mkdir(parents=False, exist_ok=True)


@log_error
def remove_dir(dst: Path) -> None:
    logging.info(f"REMOVED DIR> {dst}")
    dst.rmdir()
