import re
from src.phonimizer import g2p
from src.khmercut import tokenize
from src.texts.symbols import BOS, EOS

# Regular expression matching whitespace:
_whitespace_re = re.compile(r"\s+")

def collapse_whitespace(text: str, *args, **kwargs):
    return re.sub(_whitespace_re, " ", text)

def khmer_cleaner(text: str, add_space: bool = True) -> str:
    
    ## Split Sentences into each word, we can call segmentation
    tokens = tokenize(text=text)
    
    ## Convert normal text into phoneme format
    phonemize = g2p(
        tokens=tokens,
        use_lexicon=True,
        add_space=add_space
    )
    
    phonemize = add_bos_eos(phonemes=phonemize)
    
    phoneme_sequence = collapse_whitespace(' '.join(phonemize))
    
    return phoneme_sequence

def add_bos_eos(phonemes: list[str], *args, **kwargs):
    return [BOS] + phonemes + [EOS]