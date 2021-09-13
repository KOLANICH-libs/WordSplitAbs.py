#!/usr/bin/env python3
import itertools
import re
import sys
import unittest
from collections import OrderedDict
from pathlib import Path

dict = OrderedDict

sys.path.insert(0, str(Path(__file__).parent.parent))

from WordSplitAbs import AVAILABLE_WORD_SPLITTERS

SymSpellWordSplitter = None

try:
	from WordSplitAbs import SymSpellWordSplitter
except ImportError:
	pass

blacklistedWordSplitters = frozenset((SymSpellWordSplitter,))


class Tests(unittest.TestCase):
	testVectors = (
		"word splitting is inference of concatenated words boundaries",
		"london is a capital of great britain",
		"the quick brown fox jumps over the lazy dog",
	)
	testVectors = tuple((el.replace(" ", ""), tuple(el.split(" "))) for el in testVectors)

	WORKING_SPLITTERS = []
	BROKEN_SPLITTERS = []

	@classmethod
	def setUpClass(cls):
		print("AVAILABLE_WORD_SPLITTERS:", AVAILABLE_WORD_SPLITTERS)
		for wordSplitterCtor in AVAILABLE_WORD_SPLITTERS:
			if wordSplitterCtor not in blacklistedWordSplitters:
				cls.WORKING_SPLITTERS.append(wordSplitterCtor)
			else:
				cls.BROKEN_SPLITTERS.append(wordSplitterCtor)
		print("WORKING_SPLITTERS:", cls.WORKING_SPLITTERS)
		print("BROKEN_SPLITTERS:", cls.BROKEN_SPLITTERS)

	def _testSplittingForSplittersCtorsCollection(self, splitterCollection):
		for wordSplitterCtor in splitterCollection:
			wordSplitter = wordSplitterCtor()
			with self.subTest(wordSplitter=wordSplitter):
				for chall, etalonResp in self.__class__.testVectors:
					with self.subTest(chall=chall, etalonResp=etalonResp):
						resp = tuple(wordSplitter(chall))
						self.assertEqual(resp, etalonResp)

	@unittest.expectedFailure
	def testSplittingBlackListed(self):
		self._testSplittingForSplittersCtorsCollection(self.__class__.BROKEN_SPLITTERS)

	def testSplitting(self):
		self._testSplittingForSplittersCtorsCollection(self.__class__.WORKING_SPLITTERS)


if __name__ == "__main__":
	unittest.main()
