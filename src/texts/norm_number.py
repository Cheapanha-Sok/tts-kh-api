digit_names = ["", "មួយ", "ពីរ", "បី", "បួន", "ប្រាំ", "ប្រាំមួយ", "ប្រាំពីរ", "ប្រាំបី", "ប្រាំបួន"]
tens_names = {
    '1': "ដប់", '2': "ម្ភៃ", '3': "សាមសិប", '4': "សែសិប",
    '5': "ហាសិប", '6': "ហុកសិប", '7': "ចិតសិប", '8': "ប៉ែតសិប", '9': "កៅសិប"
}

def play_digit(digit):
    return digit_names[int(digit)] if digit in '123456789' else ""

def play_unit(pos, digit):
    return {
        10: "ពាន់",
        9: "រយ", 3: "រយ",
        8: tens_names.get(digit, ""), 2: tens_names.get(digit, ""),
        7: "លាន",
        6: "សែន",
        5: "ម៉ឺន",
        4: "ពាន់"
    }.get(pos, "")

def play_number_block(num_str):
    result = ""
    length = len(num_str)
    for i, digit in enumerate(num_str):
        pos = length - i
        if digit != '0' or pos >= 7:
            if pos not in (2, 8):
                result += play_digit(digit)
            result += play_unit(pos, digit)
    return result

def normalize_amount(amount_str: str, currency: str) -> str:
    parts = amount_str.split('.')
    amount = parts[0] if len(parts) > 0 else ""
    cents = (parts[1] + "00")[:2] if len(parts) > 1 else ""

    result = ""
    if amount:
        result += play_number_block(amount)
        result += "ដុល្លារ" if currency.upper() == "USD" else "រៀល"

    if currency.upper() == "USD" and cents and cents != "00":
        result += "ចុច" + play_number_block(cents) + "សេន"

    return result