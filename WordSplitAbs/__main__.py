import sys
from pathlib import Path, PurePath

from plumbum import cli


class CLI(cli.Application):
	"""CLI for WordSplitAbs"""


CLASS_NAME_POSTFIX = "WordSplitter"


def classNameToSplitterName(name):
	if name.endswith(CLASS_NAME_POSTFIX):
		name = name[: -len(CLASS_NAME_POSTFIX)]
	return name


@CLI.subcommand("backends")
class BackendsCLI(cli.Application):
	"""Shows available backends"""

	def main(self, *words):
		from . import AVAILABLE_WORD_SPLITTERS

		print(" ".join(classNameToSplitterName(el.__name__) for el in AVAILABLE_WORD_SPLITTERS))


@CLI.subcommand("split")
class SplitCLI(cli.Application):
	"""Splits words in a phrase"""

	__slots__ = ("splitter",)

	def generateWords(self, words):
		for w in words:
			yield from self.splitter(w)

	def main(self, *words):
		from . import ChosenWordSplitter

		print("Chosen backend: ", classNameToSplitterName(ChosenWordSplitter.__name__), file=sys.stderr)

		self.splitter = ChosenWordSplitter()
		res = []

		print(" ".join(self.generateWords(words)))


def extractDotNetAssembliesFromArchive(z: "zipfile.ZipFile"):
	import platform

	aotForOurArch = platform.architecture() == ("64bit", "ELF")

	for cfi in z.filelist:
		cfn = PurePath(cfi.filename)

		if len(cfn.parts) != 1:
			print("File not immediately in the root of archive, ignoring", cfn, file=sys.stderr)
			continue

		if cfn.name[0] == ".":
			print("Either path traversal attempt, or a hidden file, ignoring", cfn, file=sys.stderr)
			continue

		if cfn.suffix.lower() == ".dll":
			z.extract(cfi, path=Path("."), pwd=None)
			continue

		if aotForOurArch:
			if tuple(el.lower() for el in cfn.suffixes[-2:]) == (".dll", ".so"):
				z.extract(cfi, path=Path("."), pwd=None)
				continue

		if cfn.stem.lower() == "license" or cfn.suffix.lower() == ".md":
			print(str(cfn), ":", file=sys.stderr)
			sys.stderr.buffer.write(z.read(cfi))
			print(file=sys.stderr)
			continue

	return 0


@CLI.subcommand("download")
class DownloadCLI(cli.Application):
	"""Splits words in a phrase"""

	__slots__ = ()

	SOURCES = {
		"WolfGarbe_libs": ("https://github.com/KOLANICH-libs/WordSplitAbs.py/files/7161469/WordSegmentationAndSymSpell.zip", "2b64c93b6e741e0aa5832ba5f2a99c51778184e54c33805625e35a483fcd0d76", extractDotNetAssembliesFromArchive)
	}

	def main(self, what: cli.Set(*SOURCES.keys(), case_sensitive=True)):
		import hashlib
		import zipfile
		from io import BytesIO

		import requests

		uri, etalonHash, unpackerFunc = self.__class__.SOURCES[what]
		d = None
		with requests.get(uri) as r:
			d = r.content

		actualHash = hashlib.sha256(d).hexdigest().lower()
		if actualHash != etalonHash:
			print("Hash", actualHash, "doesn't mach etalon hash", etalonHash, file=sys.stderr)
			return 1

		with BytesIO(d) as f:
			with zipfile.ZipFile(f) as z:
				return unpackerFunc(z)


if __name__ == "__main__":
	CLI.run()
