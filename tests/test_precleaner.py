# !/usr/bin/env python3
import os, sys
import unittest

module_path = os.path.abspath(os.path.join('.'))
if module_path not in sys.path: sys.path.append(module_path)
from src.pre_cleaner.pre_cleaner import *

caps_sent1 = "Some CAPitalizEd letterS."
lower_sent1 = "some capitalized letters."

class PreCleanerTestCase(unittest.TestCase):

	def test_Remove_Caps(self):
		test_sent = Remove_Caps(caps_sent1)

		self.assertEqual(lower_sent1, test_sent)

	def test_Ignore_Long_Sentence(self):
		max_tokens = 5
		list_long = list(range(max_tokens + 1))
		list_short = list(range(max_tokens))
		self.assertTrue(Ignore_Long_Sentence(list_long, max_tokens))
		self.assertTrue(not Ignore_Long_Sentence(list_short, max_tokens))

if __name__ == '__main__':
	unittest.main()