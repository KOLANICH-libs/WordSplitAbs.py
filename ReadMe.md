WordSplitAbs.py [![Unlicensed work](https://raw.githubusercontent.com/unlicense/unlicense.org/master/static/favicon.png)](https://unlicense.org/)
===============
~~[wheel (GitLab)](https://gitlab.com/KOLANICH/WordSplitAbs.py/-/jobs/artifacts/master/raw/dist/WordSplitAbs-0.CI-py3-none-any.whl?job=build)~~
[wheel (GHA via `nightly.link`)](https://nightly.link/KOLANICH-libs/WordSplitAbs.py/workflows/CI/master/WordSplitAbs-0.CI-py3-none-any.whl)
~~![GitLab Build Status](https://gitlab.com/KOLANICH/WordSplitAbs.py/badges/master/pipeline.svg)~~
~~![GitLab Coverage](https://gitlab.com/KOLANICH/WordSplitAbs.py/badges/master/coverage.svg)~~
[![Coveralls Coverage](https://img.shields.io/coveralls/KOLANICH-libs/WordSplitAbs.py.svg)](https://coveralls.io/r/KOLANICH-libs/WordSplitAbs.py)
[![GitHub Actions](https://github.com/KOLANICH-libs/WordSplitAbs.py/workflows/CI/badge.svg)](https://github.com/KOLANICH-libs/WordSplitAbs.py/actions/)
[![Libraries.io Status](https://img.shields.io/librariesio/github/KOLANICH-libs/WordSplitAbs.py.svg)](https://libraries.io/github/KOLANICH-libs/WordSplitAbs.py)

This is an abstraction layer around Python libraries for splitting (tokenization) of words joined without delimiters.

It is often called `words tokenization`, but it is a bit different thing: `tokenization` is when words are naturally not splitted (in Eastern-Asian languages, for example), but `splitting` is when they are naturally splitted, but the delimiters got missed.


Tutorial
--------

```python

from WordSplitAbs import ChosenWordSplitter

s = ChosenWordSplitter()  # A resource-consuming stage, the most splitters load a corpus or a semi-preprocessed model here and infer a usable model from it. So you want to call it as less as possible.

print(s("wordsplittingisinferenceofconcatenatedwordsboundaries"))  # "word splitting is inference of concatenated words boundaries"
```

Backends
--------

| Backend | Has default corpus | Deps | Model | Quality | Notes |
|---------|--------------------|------|-------|---------|-------|
| [instant_segment](https://github.com/InstantDomain/instant-segment) | ??? |  | Unigram + bigram | Recommended | A rewrite of `wordsegment` into Rust with high performance boost |
| [wordsegment](https://github.com/grantjenks/python-wordsegment) | ?????? |  | Unigram + bigram | Recommended | |
| [WordSegmentationDP](https://github.com/wolfgarbe/WordSegmentationDP) | ??? | [pythonnet](https://github.com/pythonnet/pythonnet) + [`WordSegmentationDP.dll`](https://github.com/KOLANICH-libs/WordSplitAbs.py/files/7161469/WordSegmentationAndSymSpell.zip) + [Corpus file](https://raw.githubusercontent.com/wolfgarbe/SymSpell/master/SymSpell.FrequencyDictionary/en-80k.txt)| Unigram + Bayes | Recommended | |
| [WordSegmentationTM](https://github.com/wolfgarbe/WordSegmentationTM) | ??? | [pythonnet](https://github.com/pythonnet/pythonnet) + [`WordSegmentationTM.dll`](https://github.com/KOLANICH-libs/WordSplitAbs.py/files/7161469/WordSegmentationAndSymSpell.zip) + [Corpus file](https://raw.githubusercontent.com/wolfgarbe/SymSpell/master/SymSpell.FrequencyDictionary/en-80k.txt)| Unigram + Bayes | Recommended | |
| [SymSpell](https://github.com/wolfgarbe/SymSpell) | ??? | [pythonnet](https://github.com/pythonnet/pythonnet) + [`SymSpell.dll`](https://github.com/KOLANICH-libs/WordSplitAbs.py/files/7161469/WordSegmentationAndSymSpell.zip) + [Corpus file](https://raw.githubusercontent.com/wolfgarbe/SymSpell/master/SymSpell.FrequencyDictionary/en-80k.txt)| Unigram + Bigram | Not recommended, fails to split elementary phrases | |
| [wordninja](https://github.com/keredson/wordninja) | ?????? |  | Unigram order | Not the best quality | |
