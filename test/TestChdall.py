from contextlib import suppress
from pathlib import Path
from shutil import copy, copytree, rmtree
import os
import unittest

from chdall import *
from paths import PROJECT_ROOT

test_bin_cue_dirs = ['Ace_Combat_2__USA_', 'Advanced_V.G._2__Japan_']


class TestChdAll(unittest.TestCase):
    def setUp(self):
        # remove existing test dirs/files
        with suppress(FileNotFoundError):
            rmtree('test_dir')
        # create paths
        Path('test_dir/deeper_test_dir').mkdir(parents=True)
        project_root = Path(PROJECT_ROOT)
        # copy test files into appropriate test dirs
        copy('chdman.exe', 'test_dir')
        copytree(
            project_root / Path('Ace_Combat_2__USA_'),
            Path('test_dir') / Path('Ace_Combat_2__USA_')
        )
        copytree(
            project_root / Path('Advanced_V.G._2__Japan_'),
            Path('test_dir/deeper_test_dir') / Path('Advanced_V.G._2__Japan_')
        )
        # move into test dir
        os.chdir('test_dir')

    def tearDown(self):
        os.chdir('..')
        rmtree('test_dir')

    def test_get_all_bin_cue_dirs_from_path(self):
        self.assertEqual(set(test_bin_cue_dirs), set([p.name for p in get_all_bin_cue_dirs_from_path(os.getcwd())]))

    def test_create_chds(self):
        create_chds(os.getcwd())
        self.assertIsNotNone(find_pattern('*.chd', Path('Ace_Combat_2__USA_')))
        self.assertIsNotNone(find_pattern('*.chd', Path('deeper_test_dir/Advanced_V.G._2__Japan_')))

    def test_create_and_move_chds(self):
        create_chds(os.getcwd(), move=True)
        parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
        self.assertTrue(len(parent_dir_chds) == 2)

    def test_create_chds_and_delete_bin_cues(self):
        create_chds(os.getcwd(), move=True, remove=True)
        parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
        self.assertTrue(len(parent_dir_chds) == 2)
        self.assertFalse(Path('Ace_Combat_2__USA_').exists())
        self.assertFalse(Path('deeper_test_dir/Advanced_V.G._2__Japan_').exists())
