# -*- coding: utf-8 -*-

import unittest
import tempfile
import os

from ligabot import caching

class TestCache(unittest.TestCase):
    """Tests for the caching module"""

    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            self.file_name = tmp.name

    def tearDown(self):
        os.remove(self.file_name)

    def test_append_cache(self):
        caching.append_cache("Test1", self.file_name)
        caching.append_cache("Test2", self.file_name)
        content = open(self.file_name).read()
        self.assertEqual("Test1\nTest2\n", content)

    def test_write_cache(self):
        caching.write_cache("Testalest", self.file_name)
        content = open(self.file_name).read()
        self.assertEqual("Testalest\n", content)

    def test_read_cache(self):
        caching.write_cache("Croakaloak", self.file_name)
        content = caching.read_cache(self.file_name)
        self.assertEqual("Croakaloak\n", content)

    def test_clean_cache(self):
        caching.write_cache(" This is a test ", self.file_name)
        caching.clean_cache(self.file_name)
        content = caching.read_cache(self.file_name)
        self.assertEqual("This is a test\n", content)
