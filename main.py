import os
import sys
import shutil
from pathlib import Path
import hashlib
import argparse
import schedule
import logging
from datetime import datetime


def get_valid_abs_path(argument: str) -> Path:
    if os.path.exists(Path(argument).absolute()):
        return Path(argument).absolute()
    else:
        raise argparse.ArgumentTypeError("Directory does't exist. Provide existing directory, or create requested directory.")

def get_valid_integer(argument: str) -> int:
    if int(argument)>0:
        return int(argument)
    else:
        raise argparse.ArgumentTypeError("Sync interval is not greater than 0")

#split into seperate functions
#use decorator for logging
def handle_file(mode: str, src_root_path, rep_root_path, **kwargs) -> None:
    if 's_rel' in kwargs:
        src = Path(src_root_path,kwargs['s_rel'])
        dst = Path(rep_root_path,kwargs['s_rel'])

    if mode == "update":
        rm_dst = Path(rep_root_path, kwargs["s_rel"])
        os.remove(rm_dst)
        shutil.copy(src, dst)
        txt = 'UPDATED FILE: '
        logging.info(f"{txt:<15} {dst}")

    elif mode == "create":
        shutil.copy(src, dst)
        txt = 'CREATED FILE: '
        logging.info(f"{txt:<15} {dst}")

    elif mode == "remove":
        rm_dst = Path(rep_root_path, kwargs["r_rel"])
        os.remove(rm_dst)
        txt = 'REMOVED FILE: '
        logging.info(f"{txt:<15} {rm_dst}")

#mode handle as an enumerate
def handle_dir(mode: str, rep_root_path, rel_path) -> None:
    dst = Path(rep_root_path, rel_path)
    if mode == 'create':
        os.makedirs(dst)
        txt = 'CREATED DIR: '
        logging.info(f"{txt:<15} {dst}")
    elif mode == 'remove':
        shutil.rmtree(dst, ignore_errors=True)
        txt = 'REMOVED DIR: '
        logging.info(f"{txt:<15} {dst}")



def get_files_path_list(absolute_path: Path) -> list:
    file_list = []
    dir_list = []
    for path, subdirs, files in os.walk(absolute_path, topdown=False):
        for name in files:
            file_path = Path(Path(path).relative_to(absolute_path),name)
            file_list.append(file_path)
        for dir in subdirs:
            dir_path = Path(Path(path).relative_to(absolute_path),dir)
            if not included_in_list_parents(dir_path, dir_list):
                dir_list.append(dir_path) 

    return file_list, dir_list


def included_in_list_parents(dir_path: Path, dir_list: list) -> bool:
    for dir_i in dir_list:
        if dir_path in dir_i.parents:
            return True
    return False


def files_have_same_hash(fl1_path: Path, fl2_path: Path) -> bool:
    with open(fl1_path, 'rb') as fl1:
        with open(fl2_path, 'rb') as fl2:
            if hashlib.md5(fl1.read()).hexdigest() == hashlib.md5(fl2.read()).hexdigest():
                return True
            else:
                return False

def sync_folders(src_root_path: Path, rep_root_path: Path) -> None:
    src_files_path_list, src_dirs_path_list = get_files_path_list(src_root_path)
    rep_files_path_list, rep_dirs_path_list = get_files_path_list(rep_root_path)

    for src_dir_path in src_dirs_path_list:
        if src_dir_path not in rep_dirs_path_list:
            if not os.path.exists(rep_root_path / src_dir_path):
                handle_dir('create', rep_root_path, src_dir_path)

    for src_file_path in src_files_path_list:
        if src_file_path in rep_files_path_list:
            if not files_have_same_hash(Path(src_root_path, src_file_path),Path(rep_root_path, src_file_path)):
                handle_file("update", src_root_path, rep_root_path, s_rel=src_file_path)
        else:
            handle_file("create", src_root_path, rep_root_path, s_rel=src_file_path)

    for rep_file_path in rep_files_path_list:
        if rep_file_path not in src_files_path_list:
            handle_file("remove", src_root_path, rep_root_path, r_rel=rep_file_path)

    for rep_dir_path in rep_dirs_path_list:
        if rep_dir_path not in src_dirs_path_list:
            if not included_in_list_parents(rep_dir_path, src_dirs_path_list):
                handle_dir('remove', rep_root_path, rep_dir_path)   
  
def run_sync(src_path: Path, rep_path: Path, sync_interval: int) -> None:
    logging.info(f"***Initial info***")
    logging.info(f'Choosed source path:   {src_path}')
    logging.info(f"Choosed replica path:  {rep_path}")
    logging.info(f"Choosed sync interval: {sync_interval}s")
    logging.info(f"***Initial info***")

    schedule.every(sync_interval).seconds.do(sync_folders, src_path, rep_path)

    while True:
        schedule.run_pending()
        

def config_logging(log_path: Path) -> None:
    log_name = datetime.now().strftime("%Y_%m_%d_%H%M%S.log")
    log_path = Path(args.log_dir_path, log_name)
    #todo - string and dateformat to single variables
    logging.basicConfig(
        filename=log_path, 
        level=logging.INFO, 
        format='%(asctime)s.%(msecs)-4d || %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S')
    
    log_formatter = logging.Formatter('%(asctime)s.%(msecs)-04d || %(message)s', '%Y-%m-%d %H:%M:%S')
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(log_formatter)
    logging.getLogger().addHandler(console_handler)

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="Sync script",
        description="Program synchronizes files and directories of source folder into replica folder.",
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
        help="must be a valid directory"
    )
    parser.add_argument(
        "sync_interval",
        type=get_valid_integer,
        help="must be integer, greater than 0"
    )
    return parser

if __name__ == "__main__":
    parser = get_parser()
    args = parser.parse_args()
    config_logging(args.log_dir_path)

    try:
        run_sync(args.src_root_path, args.rep_root_path, args.sync_interval)
    except KeyboardInterrupt:
        logging.info('Program stopped manually.')
        raise SystemExit
