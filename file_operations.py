import shutil
import logging
import functools
from pathlib import Path


def log_error(func):
    """
    Decorator to log errors for the decorated function.

    Args:
        func (function): The function to be decorated.

    Returns:
        function: The wrapped function with error logging.
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")

    return wrapper


@log_error
def create_file(src: Path, dst: Path) -> None:
    """
    Create a file by copying from source to destination.

    Args:
        src (Path): The source file path.
        dst (Path): The destination file path.
    """
    logging.info(f"CREATED FILE: {dst}")
    shutil.copy(src, dst)


@log_error
def remove_file(dst: Path) -> None:
    """
    Remove a file at the given destination path.

    Args:
        dst (Path): The destination file path.
    """
    logging.info(f"REMOVED FILE: {dst}")
    dst.unlink()


@log_error
def update_file(src: Path, dst: Path) -> None:
    """
    Update a file by removing the old file and copying the new file from source to destination.

    Args:
        src (Path): The source file path.
        dst (Path): The destination file path.
    """
    logging.info(f"UPDATED FILE: {dst}")
    dst.unlink()
    shutil.copy(src, dst)


@log_error
def create_dir(dst: Path) -> None:
    """
    Create a directory at the given destination path.

    Args:
        dst (Path): The destination directory path.
    """
    logging.info(f"CREATED DIR: {dst}")
    dst.mkdir(parents=False, exist_ok=True)


@log_error
def remove_dir(dst: Path) -> None:
    """
    Remove a directory at the given destination path.

    Args:
        dst (Path): The destination directory path.
    """
    logging.info(f"REMOVED DIR: {dst}")
    dst.rmdir()
