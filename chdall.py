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


def get_all_bin_cue_dirs_from_path(path: str, bin_cue_paths: list[Path] = []) -> set[Path]:
    # returns list of Path objects for every dir and subdir in given path
    bin_cue_paths = bin_cue_paths
    for p in Path(path).iterdir():
        if p.is_dir() and not p.name.startswith('.'):
            if find_pattern('*.bin', p) and find_pattern('*.cue', p) and p not in bin_cue_paths:
                bin_cue_paths.append(p)
            get_all_bin_cue_dirs_from_path(str(p), bin_cue_paths)
    return set(bin_cue_paths)


def find_pattern(pattern: str, path: Path):
    if not path.name.startswith('.'):
        files = path.glob('*')
        for file in [f for f in files if f.is_file()]:
            if fnmatch(str(file), pattern):
                return str(file.resolve())


def create_chds(path: str, move: bool = False, remove: bool = False):
    for filepath in get_all_bin_cue_dirs_from_path(path):

        bin = find_pattern('*.bin', filepath)
        cue = find_pattern('*.cue', filepath)

        # skip files that aren't a dir and hidden files
        if not filepath.is_dir() or filepath.name.startswith('.'):
            continue

        # error handling
        if not cue or not bin:
            print(f'.cue and .bin not found in {filepath.name}!')
            continue
        else:
            cue_game_name = cue.split('.cue')[0]
        if find_pattern('*.chd', filepath):
            print(f'{filepath.name}.chd already exists!')
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
                verify_chd = subprocess.call(['chdman', 'verify', '-i', chd], stderr=subprocess.STDOUT)
                if move:
                    copy(chd, path)
                if remove:
                    rmtree(filepath)
            except subprocess.CalledProcessError as cpe:
                print(cpe.output)
                continue
            print(f'created and verified {chd}')


if __name__ == '__main__':

    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument(
        '-d', '--directory', help='Specify target directory with .bin/.cues to be converted', action='store'
    )
    arg_parser.add_argument(
        '-m', '--move', help='Move .chd files to parent folder after they are created', action='store_true'
    )
    arg_parser.add_argument(
        '-r', '--remove',
        help='Remove folder with .bin/.cue after .chd file is created, must be used with --move/-m option',
        action='store_true'
    )
    args = arg_parser.parse_args()
    target_dir = args.directory or os.getcwd()

    if not glob('chdman*'):
        raise FileNotFoundError('chdman not found!')
    if args.remove and not args.move:
        raise argparse.ArgumentError('cannot use --remove flag without --move!')
    elif args.move and args.remove:
        initial_dir_size = get_size(target_dir)
        create_chds(target_dir, args.move, args.remove)
        final_dir_size = get_size(target_dir)
        dir_size_percent_reduction = round(100 - ((final_dir_size/initial_dir_size) * 100), 2)
        print(f'initial directory size: {round(initial_dir_size/pow(1024, 3), 2)}GB')
        print(f'final directory size: {round(final_dir_size/pow(1024, 3), 2)}GB')
        print(f'{dir_size_percent_reduction}% space saved!')
    else:
        create_chds(args.move, args.remove)