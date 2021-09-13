import typing
from abc import ABC, abstractmethod
from pathlib import Path

AVAILABLE_WORD_SPLITTERS = []  # type: typing.Itterable[WordSplitter]


class NGrams:
	__slots__ = ()


class INGramsProbability(NGrams):
	__slots__ = ()

	def __init__(self, gramsWithProbs=None, orderFile: Path = None, probabilityFile: Path = None):
		raise NotImplementedError

	@property
	@abstractmethod
	def gramsWithProbs(self):
		raise NotImplementedError

	@gramsWithProbs.setter
	@abstractmethod
	def gramsWithProbs(self, v):
		raise NotImplementedError

	@property
	@abstractmethod
	def probabilityFile(self):
		raise NotImplementedError

	@probabilityFile.setter
	@abstractmethod
	def probabilityFile(self, v):
		raise NotImplementedError

	@property
	@abstractmethod
	def orderFile(self):
		raise NotImplementedError

	@orderFile.setter
	@abstractmethod
	def orderFile(self, v):
		raise NotImplementedError


def zipfLawConst(n):
	res = 0
	for i, word in range(1, n + 1):
		p = 1 / i
		res += p
	return res


def zipfLaw(n):
	k = self.zipfLawConst(n)
	for i, word in range(1, n + 1):
		yield k * 1 / i


class NGramsProbability(INGramsProbability):
	__slots__ = ("_gramsWithProbs", "_probabilityFile", "_orderFile",)

	def __init__(self, gramsWithProbs=None, orderFile: Path = None, probabilityFile: Path = None):
		#if gramsWithProbs and orderFile or gramsWithProbs and probabilityFile or orderFile and probabilityFile:
		#	raise ValueError("You must specify exactly 1 arg")

		self._gramsWithProbs = gramsWithProbs
		self._probabilityFile = probabilityFile
		self._orderFile = orderFile

	@property
	def gramsWithProbs(self):
		return self._gramsWithProbs

	@gramsWithProbs.setter
	def gramsWithProbs(self, v):
		self._gramsWithProbs = v

	@property
	def probabilityFile(self):
		return self._probabilityFile

	@probabilityFile.setter
	def probabilityFile(self, v):
		self._probabilityFile = v

	@property
	def orderFile(self):
		return self._orderFile

	@orderFile.setter
	def orderFile(self, v):
		self._orderFile = v


class WordSplittingModel:
	__slots__ = ("uni", "bi")

	def __init__(self, uni: typing.Optional[NGrams], bi: typing.Optional[NGrams]):
		self.uni = uni
		self.bi = bi


DEFAULT_MODEL = None  # type: typing.Optional[WordSplittingModel]


class WordSplitter:
	__slots__ = ("segmenter",)

	INPUT_MODEL_TYPE = (None, None)

	def __init__(self, model: typing.Optional[WordSplittingModel] = None) -> None:
		self.segmenter = None

	@abstractmethod
	def __call__(self, joinedWords: str) -> typing.Iterable[str]:
		raise NotImplementedError

	@classmethod
	@abstractmethod
	def getDefaultModel(cls) -> typing.Optional[WordSplittingModel]:
		raise NotImplementedError


ChosenWordSplitter = None  # type: WordSplitter

WordNinjaWordSplitter = None  # type: WordSplitter
try:
	import wordninja
except ImportError:
	pass
else:

	class UniGramsWordNinja(INGramsProbability):
		__slots__ = ("_orderFile", "nativeModel", "_gramsWithProbs")
		DEFAULT_UNIGRAMS_FILE = Path(wordninja.__file__).parent / "wordninja_words.txt.gz"

		def __init__(self, gramsWithProbs=None, orderFile: Path = None, probabilityFile: Path = None):
			self._gramsWithProbs = None
			if orderFile is None and gramsWithProbs is None and probabilityFile is None:
				self._orderFile = self.__class__.DEFAULT_UNIGRAMS_FILE
				self.nativeModel = wordninja.DEFAULT_LANGUAGE_MODEL
			else:
				if orderFile:
					self._orderFile = orderFile
					self.nativeModel = wordninja.LanguageModel(orderFile)

		def genGramsWithProbs(self):
			for word, p in zip(wordninja.DEFAULT_LANGUAGE_MODEL._wordcost.keys(), zipfLaw(len(wordninja.DEFAULT_LANGUAGE_MODEL._wordcost))):
				yield (word, p)

		@property
		def gramsWithProbs(self):
			if self._gramsWithProbs is None:
				self._gramsWithProbs = tuple(self.genGramsWithProbs())
			return self._gramsWithProbs

		@gramsWithProbs.setter
		def gramsWithProbs(self, v):
			self._gramsWithProbs = v

	class OurWordNinjaLanguageModel(wordninja.LanguageModel):
		def __init__(self, model: WordSplittingModel):
			from math import log

			maxW = None
			maxWLen = 0
			wds = []
			for w, p in model.uni.gramsWithProbs:
				wds.append((w, -log(p)))
				l = len(w)
				if maxWLen < l:
					maxW = w
					maxWLen = l
			self._wordcost = tuple(sorted(wds))
			self._maxword = maxW

	class WordNinjaWordSplitter(WordSplitter):
		__slots__ = ()

		@classmethod
		def getDefaultModel(cls) -> WordSplittingModel:
			return WordSplittingModel(UniGramsWordNinja(), None)

		def __init__(self, model: typing.Optional[WordSplittingModel] = None) -> None:
			super().__init__()
			if not model:
				self.segmenter = wordninja.DEFAULT_LANGUAGE_MODEL
			else:
				self.segmenter = OurWordNinjaLanguageModel(model)


		def __call__(self, joinedWords: str) -> typing.Iterable[str]:
			return wordninja.split(joinedWords)

	ChosenWordSplitter = WordNinjaWordSplitter
	AVAILABLE_WORD_SPLITTERS.append(WordNinjaWordSplitter)
	DEFAULT_MODEL = WordNinjaWordSplitter.getDefaultModel()


WordSegmentationTMWordSplitter = None  # type: WordSplitter
SymSpellWordSplitter = None  # type: WordSplitter

try:
	import clr
	from System.IO import FileNotFoundException as CLRFileNotFoundException
except ImportError:
	pass
else:
	kindaDefaultCorpusFilePath = "SymSpell.FrequencyDictionary/en-80k.txt"

	try:
		symSpellAssembly = clr.AddReference("SymSpell")
	except CLRFileNotFoundException:
		pass
	else:
		SymSpell = clr.SymSpell

		class SymSpellWordSplitter(WordSplitter):
			__slots__ = ()

			def __init__(self, model: typing.Optional[WordSplittingModel] = None) -> None:
				if model is None:
					model = DEFAULT_MODEL

				if model is None:
					raise ValueError("This splitter has no own default model")

				super().__init__()
				self.segmenter = SymSpell()
				self.segmenter.LoadDictionary(str(corpusFilePath), 0, 1)
				# CreateDictionaryEntry(string key, Int64 count)

			def __call__(self, joinedWords: str) -> typing.Iterable[str]:
				return self.segmenter.WordSegmentation(joinedWords).Item1.split(" ")

			@classmethod
			def getDefaultModel(cls) -> typing.Optional[WordSplittingModel]:
				return None

		ChosenWordSplitter = SymSpellWordSplitter
		AVAILABLE_WORD_SPLITTERS.append(SymSpellWordSplitter)

	class WordSegmentationWordSplitter(WordSplitter):
		__slots__ = ()
		CTOR = None

		def __init__(self, model: WordSplittingModel = None) -> None:
			super().__init__()
			self.segmenter = self.__class__.CTOR()
			self.segmenter.LoadDictionary(str(corpusFilePath), 0, 1)

		def __call__(self, joinedWords: str) -> typing.Iterable[str]:
			return self.segmenter.Segment(joinedWords).Item1.split(" ")

		@classmethod
		def getDefaultModel(cls) -> typing.Optional[WordSplittingModel]:
			return None

	try:
		WordSegmentationTMAssembly = clr.AddReference("WordSegmentationTM")
	except CLRFileNotFoundException:
		pass
	else:

		class WordSegmentationTMWordSplitter(WordSegmentationWordSplitter):
			__slots__ = ()
			CTOR = clr.WordSegmentationTM

		ChosenWordSplitter = WordSegmentationTMWordSplitter
		AVAILABLE_WORD_SPLITTERS.append(WordSegmentationTMWordSplitter)

	try:
		WordSegmentationTMAssembly = clr.AddReference("WordSegmentationDP")
	except CLRFileNotFoundException:
		pass
	else:

		class WordSegmentationDPWordSplitter(WordSegmentationWordSplitter):
			__slots__ = ()
			CTOR = clr.WordSegmentationDP

		ChosenWordSplitter = WordSegmentationDPWordSplitter
		AVAILABLE_WORD_SPLITTERS.append(WordSegmentationDPWordSplitter)


class WordSegmentWordSplitterBase(WordSplitter):
	__slots__ = ()
	CTOR = None
	INPUT_MODEL_TYPE = (NGramsProbability, None)

	def __init__(self, model: typing.Optional[WordSplittingModel] = None) -> None:
		super().__init__()
		self.segmenter = self.__class__.CTOR()

		if model is None:
			self.segmenter.load()
		else:
			self.setModel()

	def setModel(self, WordSplittingModel) -> None:
		raise NotImplementedError

	def __call__(self, joinedWords: str) -> typing.Iterable[str]:
		return self.segmenter.segment(joinedWords)


WordSegmentWordSplitter = None  # type: WordSplitter
InstantSegmentWordSplitter = None  # type: WordSplitter

try:
	import wordsegment
except ImportError:
	pass
else:

	class WordSegmentWordSplitter(WordSegmentWordSplitterBase):
		__slots__ = ()
		CTOR = wordsegment.Segmenter

		def setModel(self, model: WordSplittingModel) -> None:
			self.splitter.unigrams.update(dict(model.ug))
			self.splitter.bigrams.update({" ".join(words): prob for (words, prob) in model.bg})
			self.splitter.total = self.TOTAL
			self.splitter.limit = self.LIMIT
			self.splitter.words.extend(text.splitlines())

		@classmethod
		def getDefaultModel(cls) -> WordSplittingModel:
			ugs = NGramsProbability(gramsWithProbs=tuple(wordsegment.Segmenter.parse(wordsegment.Segmenter.UNIGRAMS_FILENAME).items()), probabilityFile=Path(wordsegment.Segmenter.UNIGRAMS_FILENAME))
			bigs = NGramsProbability(gramsWithProbs=tuple((tuple(k.split(" ")), v) for (k, v) in wordsegment.Segmenter.parse(wordsegment.Segmenter.BIGRAMS_FILENAME).items()), probabilityFile=Path(wordsegment.Segmenter.BIGRAMS_FILENAME))
			return WordSplittingModel(ugs, bigs)

	ChosenWordSplitter = WordSegmentWordSplitter
	AVAILABLE_WORD_SPLITTERS.append(WordSegmentWordSplitter)
	DEFAULT_MODEL = WordSegmentWordSplitter.getDefaultModel()


try:
	import instant_segment
except ImportError:
	pass
else:

	class InstantSegmentWordSegmentLikeWrapper:
		__slots__ = ("segmenter", "model")

		def __init__(self, model: WordSplittingModel = None):
			if model is None:
				model = DEFAULT_MODEL

			self.model = model

			ugs = self.model.uni.gramsWithProbs
			bigs = self.model.bi.gramsWithProbs
			self.segmenter = instant_segment.Segmenter(iter(ugs), iter(bigs))

		def segment(self, text: str) -> typing.Iterable[str]:
			search = instant_segment.Search()
			res = self.segmenter.segment(text, search)
			return search

	class InstantSegmentWordSplitter(WordSegmentWordSplitterBase):
		__slots__ = ()
		CTOR = InstantSegmentWordSegmentLikeWrapper

		def __init__(self, model: WordSplittingModel = None):
			self.segmenter = InstantSegmentWordSegmentLikeWrapper(model)

		@classmethod
		def getDefaultModel(cls) -> WordSplittingModel:
			raise NotImplementedError("This splitter has no own default model")

	ChosenWordSplitter = InstantSegmentWordSplitter
	AVAILABLE_WORD_SPLITTERS.append(InstantSegmentWordSplitter)


AVAILABLE_WORD_SPLITTERS = tuple(AVAILABLE_WORD_SPLITTERS)

__all__ = tuple(el.__name__ for el in AVAILABLE_WORD_SPLITTERS)
