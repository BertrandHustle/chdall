import argparse
import os
import subprocess
from fnmatch import fnmatch
from pathlib import Path
from shutil import move, rmtree


def find_pattern(pattern, path):
    if not path.startswith('.'):
        files = Path(path).glob('*')
        for file in [f for f in files if f.is_file()]:
            if fnmatch(file, pattern):
                return str(file.resolve())


def get_size_diff(bytes_bigger, bytes_smaller):
    size_diff = bytes_bigger - bytes_smaller
    byte_mapping = {1: 'kb', 2: 'mb', 3: 'gb'}
    i = 0
    while len(str(size_diff)) != 4:
        size_diff = size_diff << 10
        i += 1
    return size_diff, byte_mapping


def move_chds(remove: bool = False):
    for filepath in os.listdir():
        chd = find_pattern('*.chd', filepath)
        if chd:
            move(chd, os.curdir)
            if remove:
                rmtree(filepath)


def create_chds():
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
                ['chdman.exe', 'createcd', '-i', cue, '-o', f'{cue_game_name}.chd'], stderr=subprocess.STDOUT
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
                verify_chd = subprocess.check_output(['chdman.exe', 'verify', '-i', chd], stderr=subprocess.STDOUT)
            except subprocess.CalledProcessError as cpe:
                print(cpe.output)
                continue
            print(f'created and verified {chd}')


if __name__ == '__main__':

    initial_dir_size = os.path.getsize(os.getcwd())

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

    if not os.path.exists('chdman.exe'):
        raise FileNotFoundError('chdman.exe not found!')
    create_chds()
    if args.move:
        move_chds(args.delete)
    if args.delete:
        final_dir_size = os.path.getsize(os.getcwd())
        dir_size_percentage = (initial_dir_size - final_dir_size) * 100
        print(f'{dir_size_percentage}% space saved!')