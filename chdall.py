import fnmatch
import os
import subprocess


def find_pattern(pattern, path):
    # https://stackoverflow.com/a/1724723/6237477
    for root, dirs, files in os.walk(path):
        for name in files:
            if fnmatch.fnmatch(name, pattern):
                return os.path.join(root, name)


def convert_chds():
    for filepath in os.listdir() :

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

        # make sure we succeeded
        chd = find_pattern('*.chd', filepath)
        if not chd:
            print(f'.chd not created! errors: {chdman_cmd}')
        else:
            print(chdman_cmd)
        #TODO: find out if we can zip chds


if __name__ == '__main__':
    if not os.path.exists('chdman.exe'):
        raise FileNotFoundError('chdman.exe not found!')
    convert_chds()
