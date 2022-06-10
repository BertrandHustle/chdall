from shutil import copytree, rmtree
import os
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

    def test_create_chds(self):
        create_chds()
        for d in test_bin_cue_dirs:
            self.assertIsNotNone(find_pattern('*.chd', d))

    def test_create_and_move_chds(self):
        create_chds(move=True)
        parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
        self.assertTrue(len(parent_dir_chds) == 2)

    def test_create_chds_and_delete_bin_cues(self):
        create_chds(move=True, delete=True)
        parent_dir_chds = [f for f in os.listdir() if f.endswith('.chd')]
        self.assertTrue(len(parent_dir_chds) == 2)
        for d in test_bin_cue_dirs:
            self.assertFalse(os.path.exists(d))
