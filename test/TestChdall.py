from chdall import *


def test_move_chds():
    create_chds()
    move_chds()
    parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
    assert len(parent_dir_chds) == 2


