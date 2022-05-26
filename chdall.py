import argparse
import os
import subprocess
from fnmatch import fnmatch
from shutil import move, rmtree


def find_pattern(pattern, path):
    # https://stackoverflow.com/a/1724723/6237477
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch(name, pattern):
                return os.path.join(root, name)


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

    if not os.path.exists('chdman.exe'):
        raise FileNotFoundError('chdman.exe not found!')
    create_chds()
    if arg_parser.move:
        move_chds(arg_parser.delete)
    if arg_parser.delete:
        final_dir_size = os.path.getsize(os.getcwd())
        dir_size_diff = initial_dir_size - final_dir_size
        print()