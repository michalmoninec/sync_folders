import os
import sys
import shutil
from pathlib import Path
import hashlib
import argparse
from typing import List
import schedule
import logging
from datetime import datetime
from utils import create_file, remove_file, update_file, create_dir, remove_dir


def get_valid_abs_path(argument: str) -> Path:
    if Path(argument).absolute().exists():
        return Path(argument).absolute()
    else:
        raise argparse.ArgumentTypeError(
            "Directory does't exist. \n"
            "Provide existing directory, or create requested directory."
        )

def get_valid_interval(argument: str) -> int:
    if int(argument)>0:
        return int(argument)
    else:
        raise argparse.ArgumentTypeError("Sync interval is not greater than 0")

def files_have_same_hash(fl1_path: Path, fl2_path: Path) -> bool:
    with open(fl1_path, 'rb') as fl1:
        with open(fl2_path, 'rb') as fl2:
            if hashlib.md5(
                fl1.read()).hexdigest() == hashlib.md5(fl2.read()).hexdigest():
                return True
            else:
                return False

def create_directories(src_dir: Path, rep_dir: Path) -> None:
    for path in src_dir.glob("*/**"):
        p_rel = rep_dir / path.relative_to(src_dir)
        if not p_rel.exists():
            create_dir(p_rel)

def remove_directories(src_dir: Path, rep_dir: Path) -> None:
    remove_paths = []
    for path in rep_dir.glob("*/**"):
        p_rel = src_dir / path.relative_to(rep_dir)
        if not p_rel.exists():
            remove_paths.append(path)

    for path in remove_paths:
        remove_dir(path)

def create_files (src_dir: Path, rep_dir: Path) -> None:
    for path in src_dir.glob("**/*.*"):
        p_rel = rep_dir / path.relative_to(src_dir)
        if p_rel.exists():
            if not files_have_same_hash(path, p_rel):
                update_file(path, p_rel)
        else:
            create_file(path, p_rel)

def remove_files (src_dir: Path, rep_dir: Path) -> None:
    remove_paths = []
    for path in rep_dir.glob("**/*.*"):
        p_rel = src_dir / path.relative_to(rep_dir)
        if not p_rel.exists():
            remove_paths.append(path)
    for path in remove_paths:
        remove_file(path)

def sync_folders(src_root_path: Path, rep_root_path: Path) -> None:
    #change to glob
    create_directories(src_root_path, rep_root_path)
    create_files(src_root_path, rep_root_path)
    remove_files(src_root_path, rep_root_path)
    remove_directories(src_root_path, rep_root_path)

def keyboard_interrupt_handle(func):
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
        except KeyboardInterrupt:
            logging.info('Program stopped manually.')
            raise SystemExit
        return func
    return wrapper

@keyboard_interrupt_handle
def run_sync(src_path: Path, rep_path: Path, sync_interval: int) -> None:
    logging.info(f"***Initial info***")
    logging.info(f'Choosed source path:   {src_path}')
    logging.info(f"Choosed replica path:  {rep_path}")
    logging.info(f"Choosed sync interval: {sync_interval}s")
    logging.info(f"***Initial info***")
    schedule.every(sync_interval).seconds.do(
        sync_folders, src_path, rep_path
    )

    while True:
        schedule.run_pending()
        

def config_logging(log_path: Path) -> None:
    log_name = datetime.now().strftime("%Y_%m_%d_%H%M%S.log")
    log_path = Path(args.log_dir_path, log_name)
    #TODO - string and dateformat to single variables. messy
    logging.basicConfig(
        filename=log_path, 
        level=logging.INFO, 
        format='%(asctime)s.%(msecs)-4d || %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    log_formatter = logging.Formatter(
        '%(asctime)s.%(msecs)-04d || %(message)s', 
        '%Y-%m-%d %H:%M:%S'
    )
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(console_handler)

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Sync script",
        description="Program synchronizes files \n"
                    "and directories of source folder into replica folder.",
        epilog="Happy syncing."
    )
    parser.add_argument(
        "src_root_path",
        type=get_valid_abs_path,
        help="must be a valid directory"
    )
    parser.add_argument(
        "rep_root_path",
        type=get_valid_abs_path,
        help="must be a valid directory"
    )
    parser.add_argument(
        "log_dir_path",
        type=get_valid_abs_path,
        help="must be a valid directory, different than src and rep"
    )
    parser.add_argument(
        "sync_interval",
        type=get_valid_interval,
        help="must be integer, greater than 0"
    )
    return parser

def validate_args() -> None:
    pass

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    validate_args()

    config_logging(args.log_dir_path)

    run_sync(args.src_root_path, args.rep_root_path, args.sync_interval)

