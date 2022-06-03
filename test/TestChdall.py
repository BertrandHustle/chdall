from shutil import copy, copytree, rmtree
import os
import pathlib
import unittest

from chdall import *
from paths import PROJECT_ROOT

test_bin_cue_dirs = ['Ace_Combat_2__USA_', 'Advanced_V.G._2__Japan_']


class TestChdAll(unittest.TestCase):
    def setUp(self):
        os.chdir('test_dir')
        self._remove_test_dirs_and_chds()
        for d in test_bin_cue_dirs:
            copytree(
                os.path.join(PROJECT_ROOT, d),
                os.path.join(os.getcwd(), d)
            )

    def tearDown(self):
        self._remove_test_dirs_and_chds()
        os.chdir('..')

    # specific setup/teardown methods

    @staticmethod
    def _remove_test_dirs_and_chds():
        for f in os.listdir():
            if f in test_bin_cue_dirs:
                rmtree(f)
            elif f.endswith('.chd'):
                os.remove(f)

    @staticmethod
    def _copy_test_chds():
        for d in test_bin_cue_dirs:
            cue = find_pattern('*.cue', os.path.join(PROJECT_ROOT, d))
            cue_path = pathlib.PurePath(cue)
            chd_prefix = cue_path.name.replace('.cue', '.chd')
            source_chd = pathlib.PurePath(PROJECT_ROOT, 'test', 'test_chds', chd_prefix)
            copy(source_chd, os.path.join(d, chd_prefix))

    def test_get_size_diff(self):
        test_mapping = {
            0: (1, 'b'),
            1: (1023, 'kb'),
            2: (1023000, 'mb'),
            3: (1023334440, 'gb')
        }
        for i in range(4):
            smaller = i
            bigger = pow(1024, i)
            print(get_size_diff(smaller, bigger))

    def test_create_chds(self):
        create_chds()
        for d in test_bin_cue_dirs:
            self.assertIsNotNone(find_pattern('*.chd', d))

    def test_move_chds(self):
        self._copy_test_chds()
        move_chds()
        parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
        self.assertTrue(len(parent_dir_chds) == 2)

    def test_delete_bin_cues(self):
        self._copy_test_chds()
        move_chds(remove=True)
        parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
        self.assertTrue(len(parent_dir_chds) == 2)
        for d in test_bin_cue_dirs:
            self.assertFalse(os.path.exists(d))
