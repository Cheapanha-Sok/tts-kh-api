from src.texts.cleaners import khmer_cleaner

def text_to_sequence(text, symbol_ids: list[dict[int, str]]):
    sequence = []
    clean_text = khmer_cleaner(text)
    for symbol in clean_text.strip().split():
        if symbol in symbol_ids:
            sequence.append(symbol_ids[symbol])
        else:
            print(f"[Warning] Symbol not found: {symbol}")
    return sequence