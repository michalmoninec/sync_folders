import os
import sys
from pathlib import Path
import hashlib
import argparse
import schedule
import logging
from datetime import datetime
from file_operations import (
    create_file,
    remove_file,
    update_file,
    create_dir,
    remove_dir,
)


def files_have_same_hash(fl1_path: Path, fl2_path: Path, chunk_size: int) -> bool:
    with open(fl1_path, "rb") as fl1, open(fl2_path, "rb") as fl2:
        while True:
            chunk1 = fl1.read(chunk_size)
            chunk2 = fl2.read(chunk_size)

            if not chunk1 and not chunk2:
                return True

            if not chunk1 or not chunk2:
                return False

            hash_fl1 = hashlib.md5(fl1.read(chunk_size)).hexdigest()
            hash_fl2 = hashlib.md5(fl2.read(chunk_size)).hexdigest()

            if hash_fl1 != hash_fl2:
                return False


def create_directories(src_dir: Path, rep_dir: Path) -> None:
    for path in src_dir.glob("*/**"):
        p_rel = rep_dir / path.relative_to(src_dir)
        if not p_rel.exists():
            create_dir(p_rel)


def create_files(src_dir: Path, rep_dir: Path, chunk_size: int) -> None:
    for path in src_dir.glob("**/*.*"):
        p_rel = rep_dir / path.relative_to(src_dir)
        if p_rel.exists():
            if not files_have_same_hash(path, p_rel, chunk_size):
                update_file(path, p_rel)
        else:
            create_file(path, p_rel)


def remove_files(src_dir: Path, rep_dir: Path) -> None:
    for path in rep_dir.glob("**/*.*"):
        p_rel = src_dir / path.relative_to(rep_dir)
        if not p_rel.exists():
            remove_file(path)


def remove_directories(src_dir: Path, rep_dir: Path) -> None:
    rm_paths = []
    for path in rep_dir.glob("*/**"):
        p_rel = src_dir / path.relative_to(rep_dir)
        if not p_rel.exists():
            rm_paths.append(path)

    for path in rm_paths[::-1]:
        remove_dir(path)


def keyboard_interrupt_handle(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt as e:
            logging.info("Program stopped manually.")
            raise e
        return func

    return wrapper


@keyboard_interrupt_handle
def run_sync(
    src_path: Path, rep_path: Path, sync_interval: int, chunk_size: int
) -> None:
    logging.info(f"***Initial info***")
    logging.info(f"Choosed source path:   {src_path}")
    logging.info(f"Choosed replica path:  {rep_path}")
    logging.info(f"Choosed sync interval: {sync_interval}s")
    logging.info(f"***Initial info***")
    schedule.every(sync_interval).seconds.do(
        sync_folders, src_path, rep_path, chunk_size
    )

    while True:
        schedule.run_pending()


def sync_folders(src_root_path: Path, rep_root_path: Path, chunk_size: int) -> None:
    create_directories(src_root_path, rep_root_path)
    create_files(src_root_path, rep_root_path, chunk_size)
    remove_files(src_root_path, rep_root_path)
    remove_directories(src_root_path, rep_root_path)


def config_logging(log_path: Path) -> None:
    log_name = datetime.now().strftime("%Y_%m_%d_%H%M%S.log")
    log_path = Path(args.log_dir_path, log_name)
    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s.%(msecs)-4d || %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    log_formatter = logging.Formatter(
        "%(asctime)s.%(msecs)-04d || %(message)s", "%Y-%m-%d %H:%M:%S"
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(console_handler)


def get_valid_abs_path(argument: str) -> Path:
    if Path(argument).absolute().exists():
        return Path(argument).absolute()
    else:
        raise argparse.ArgumentTypeError(
            "Directory does't exist. \n"
            "Provide existing directory, or create requested directory."
        )


def get_valid_positive_integer(arg: str, context: str) -> int:
    if int(arg) > 0:
        return int(arg)
    else:
        raise argparse.ArgumentTypeError(f"{context} must be greater than 0")


def validate_args(
    parser: argparse.ArgumentParser,
    src: Path,
    rep: Path,
    log: Path,
) -> None:

    if log == src or log == rep:
        raise parser.error("Log direcotry cannot be the same as source of rep")

    if src in log.parents or rep in log.parents:
        raise parser.error("Log directory cannot be inside source or replica folder")


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Sync script",
        description="Program synchronizes files \n"
        "and directories of source folder into replica folder.",
        epilog="Happy syncing.",
    )
    parser.add_argument(
        "src_root_path", type=get_valid_abs_path, help="must be a valid directory"
    )
    parser.add_argument(
        "rep_root_path", type=get_valid_abs_path, help="must be a valid directory"
    )
    parser.add_argument(
        "log_dir_path",
        type=get_valid_abs_path,
        help="must be a valid directory, different than src and rep",
    )
    parser.add_argument(
        "sync_interval",
        type=lambda arg: get_valid_positive_integer(arg, "Sync interval"),
        help="must be integer, greater than 0",
    )
    parser.add_argument(
        "chunk_size",
        type=lambda arg: get_valid_positive_integer(arg, "Chunk size"),
        default=1024,
        help="chunk size of files when compared, must be greater than zero",
    )
    return parser


if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()

    validate_args(
        parser,
        args.src_root_path,
        args.rep_root_path,
        args.log_dir_path,
        args.chunk_size,
    )

    config_logging(args.log_dir_path)

    run_sync(
        args.src_root_path, args.rep_root_path, args.sync_interval, args.chunk_size
    )
