from unittest import TestCase
from move import load_target_dirs, load_target_extensions


class TestLoadTargetDirs(TestCase):
    def test_load_target_dirs_test_file(self):
        self.assertEqual(load_target_dirs('tests/targets.txt'), [
                         'C:\\Users\\Example\\Downloads', 'C:\\Users\\Example\\Desktop'])


class TestLoadTargetExtensions(TestCase):
    def test_load_target_extensions_test_file(self):
        self.assertEqual(load_target_extensions('tests/extensions.txt'), [
                         'jpeg', 'jpg', 'png', 'mp4'])
