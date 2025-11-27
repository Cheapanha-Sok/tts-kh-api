import os
import csv
from sosap import Model

def _read_lexicon_file(file):
    lexicon = {}
    with open(file) as infile:
        for line in csv.reader(infile, delimiter="\t"):
            word, phonemes = line
            word, phonemes = word.strip(), phonemes.strip().split()
            lexicon[word] = phonemes
    return lexicon

def _save_new_phonemes(file: str, word: str, new_phoneme: list[str]):
    phoneme_str = " ".join(new_phoneme)
    with open(file, "a", encoding="utf-8") as outfile:
        outfile.write(f"{word}\t{phoneme_str}\n")  # ← make sure there's \n here
    print(f"Save New Phoneme Successfully: {word} -> {phoneme_str}")

_model_file = os.path.join(os.path.dirname(__file__), "model.fst")
_lexicon_file = os.path.join(os.path.dirname(__file__), "lexicon.tsv")
_space = '<space>'
_lexicon_dict = _read_lexicon_file(_lexicon_file)
_model = Model(_model_file)

def lowercase(text: str, *args, **kwargs):
    return text.lower()

def _phoneticize(word: str):
    results = _model.phoneticize(word)
    return results

def g2p_single(word, use_lexicon: bool = True):
    lowercase_word = lowercase(word)
    if use_lexicon and lowercase_word in _lexicon_dict:
        return _lexicon_dict[lowercase_word]
    phonemes = _phoneticize(lowercase_word)
    _save_new_phonemes(file=_lexicon_file , word=lowercase_word, new_phoneme=phonemes)
    return phonemes

def g2p(tokens: list[str], use_lexicon: bool, add_space: bool = True):
    out_puts = []
    for word in tokens:
        phonemes = g2p_single(lowercase(word), use_lexicon=use_lexicon)
        out_puts.extend(phonemes)
        if add_space and word != tokens[-1]:
            out_puts.append(_space)
    return out_puts
