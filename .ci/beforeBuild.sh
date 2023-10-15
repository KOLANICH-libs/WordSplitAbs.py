#!/usr/bin/env sh

python3 -m WordSplitAbs download WolfGarbe_libs;
mkdir -p ./SymSpell.FrequencyDictionary;
wget -O ./SymSpell.FrequencyDictionary/en-80k.txt https://raw.githubusercontent.com/wolfgarbe/SymSpell/master/SymSpell.FrequencyDictionary/en-80k.txt;
