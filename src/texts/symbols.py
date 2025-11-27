_punctuation = ['_','.']
_special_symbols = ['<pad>', '<unk>', '<bos>', '<eos>', '<space>', '<laugh>']
_letters_ipa = ['n', 'k', 'm', 't', 'p', 'r', 'aa', 'c', 'ʔ', 'a', 's', 'l', 'ŋ', 'ɑ', 'ie', 'j', 'h', 'w', 'u', 'ɓ', 'ɨ', 'ii', 'ɗ', 'ə', 'o', 'oo', 'ae', 'uə', 'ee', 'ea', 'th', 'ɲ', 'ɑɑ', 'oa', 'e', 'i', 'ph', 'aə', 'əə', 'uu', 'kh', 'ɔ', 'iə', 'ɔɔ', 'ao', 'ɛɛ', 'ch', 'f', 'ɨɨ', 'ɨə', 'g', 'z', 'ɛə', 'ɛ']

# Export all symbo
symbols = _punctuation + _special_symbols + _letters_ipa
BOS, EOS = symbols[4], symbols[5]