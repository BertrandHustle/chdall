import argparse
import fnmatch
import os
import subprocess


def find_pattern(pattern, path):
    # https://stackoverflow.com/a/1724723/6237477
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)


if not os.path.exists('chdman.exe'):
    raise FileNotFoundError('chdman.exe not found!')

for filepath in os.listdir():
    bin = find_pattern('*.bin', filepath)
    cue = find_pattern('*.cue', filepath)
    bin_game_name = bin.split('.cue')[0]
    cue_game_name = cue.split('.cue')[0]
    # error handling
    if not cue or not bin:
        print(f'.cue and .bin not found in {filepath}!')
        continue
    if bin_game_name != cue_game_name:
        print(f'.cue and .bin names in {filepath} don\`t match!')
        continue

    chdman_cmd = subprocess.check_output(f'chdman.exe -i {cue} -o {cue_game_name}.chd'.split(' '))

    # make sure we succeeded
    chd = find_pattern('*.chd', filepath)
    if not chd:
        print(f'.chd not created! errors: {chdman_cmd}')
    #TODO: find out if we can zip chds
