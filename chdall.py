import argparse
import os
import subprocess
from fnmatch import fnmatch
from glob import glob
from pathlib import Path
from shutil import copy, rmtree


def get_size(path: str):
    # https://stackoverflow.com/a/1392549/6237477
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(path):
        for f in filenames:
            fp = os.path.join(dirpath, f)
            # skip if it is symbolic link
            if not os.path.islink(fp):
                total_size += os.path.getsize(fp)
    return total_size


def find_pattern(pattern: str, path: str):
    if not path.startswith('.'):
        files = Path(path).glob('*')
        for file in [f for f in files if f.is_file()]:
            if fnmatch(file, pattern):
                return str(file.resolve())


def create_chds(move: bool = False, delete: bool = False):
    for filepath in os.listdir():

        bin = find_pattern('*.bin', filepath)
        cue = find_pattern('*.cue', filepath)

        # skip files that aren't a dir and hidden files
        if not os.path.isdir(filepath) or filepath.startswith('.'):
            continue

        # error handling
        if not cue or not bin:
            print(f'.cue and .bin not found in {filepath}!')
            continue
        else:
            cue_game_name = cue.split('.cue')[0]
        if find_pattern('*.chd', filepath):
            print(f'{filepath}.chd already exists!')
            continue

        # execute chdman
        try:
            chdman_cmd = subprocess.check_output(
                ['chdman', 'createcd', '-i', cue, '-o', f'{cue_game_name}.chd'], stderr=subprocess.STDOUT
            )
        except subprocess.CalledProcessError as cpe:
            print(cpe.output)
            continue

        # make sure we succeeded
        chd = find_pattern('*.chd', filepath)
        if not chd:
            print(f'.chd not created! errors: {chdman_cmd}')
            continue
        else:
            try:
                verify_chd = subprocess.check_output(['chdman', 'verify', '-i', chd], stderr=subprocess.STDOUT)
                if move:
                    copy(chd, os.curdir)
                if delete:
                    rmtree(filepath)
            except subprocess.CalledProcessError as cpe:
                print(cpe.output)
                continue
            print(f'created and verified {chd}')


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-m', '--move', help='Move .chd files to parent folder after they are created', action='store_true'
    )
    arg_parser.add_argument(
        '-d', '--delete',
        help='Delete folder with .bin/.cue after .chd file is created, must be used with --move/-m option',
        action='store_true'
    )
    args = arg_parser.parse_args()

    if not glob('chdman*'):
        raise FileNotFoundError('chdman not found!')
    if args.delete and not args.move:
        raise argparse.ArgumentError('cannot use --delete flag without --move!')
    elif args.move and args.delete:
        initial_dir_size = get_size(os.getcwd())
        create_chds(args.move, args.delete)
        final_dir_size = get_size(os.getcwd())
        dir_size_percent_reduction = round(100 - ((final_dir_size/initial_dir_size) * 100), 2)
        print(f'initial directory size: {round(initial_dir_size/pow(1024, 3), 2)}GB')
        print(f'final directory size: {round(final_dir_size/pow(1024, 3), 2)}GB')
        print(f'{dir_size_percent_reduction}% space saved!')
    else:
        create_chds(args.move, args.delete)