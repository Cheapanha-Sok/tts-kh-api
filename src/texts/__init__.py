from src.texts.symbols import symbols
from src.texts.cleaners import khmer_cleaner

# Mappings from symbol to numeric ID and vice versa:
_symbol_to_id = {s: i for i, s in enumerate(symbols)}

def text_to_sequence(text):
    sequence = []
    clean_text = khmer_cleaner(text)
    for symbol in clean_text.strip().split():
        if symbol in _symbol_to_id:
            sequence.append(_symbol_to_id[symbol])
        else:
            print(f"[Warning] Symbol not found: {symbol}")
    return sequence