# chdall
Script that converts bin/cues in sub-directories to .chd files

REQUIREMENTS:
- Python 3.x 
- chdman
  - Windows: chdman.exe is included in all Mame binary packages
  - Mac: `brew install rom-tools`
  - Linux (only tested on Ubuntu): `apt get mame-tools`

USAGE:
1. place chdall.py and chdman.exe in directory with sub-directories of .bin/.cues
2. `python chdall.py`

FLAGS:

--directory/-d: Specify target directory with .bin/.cues to be converted

--move/-m: Move .chd files to parent folder after they are created

--remove/-r: Delete folder with .bin/.cue after .chd file is created, must be used with --move/-m option
