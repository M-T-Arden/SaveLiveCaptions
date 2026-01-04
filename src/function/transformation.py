import re

# 
NUM_WORDS = {
    "zero": 0, "one": 1, "two": 2, "three": 3, "four": 4,
    "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9,
    "ten": 10, "eleven": 11, "twelve": 12, "thirteen": 13,
    "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17,
    "eighteen": 18, "nineteen": 19, "twenty": 20, "thirty": 30,
    "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70,
    "eighty": 80, "ninety": 90,
    "hundred": 100, "thousand": 1000,
    "a": 1, "oh": 0
}


# 21st → 21
def strip_ordinal_suffix(word):
    if word.endswith(("st", "nd", "rd", "th")):
        base = word[:-2]
        if base.isdigit():
            return base
    return word


def parse_number_phrase(words):
    total = 0
    current = 0

    for w in words:

        if w in NUM_WORDS:
            val = NUM_WORDS[w]

            # oh ：twenty oh eight → 2008
            if w == "oh" and current >= 10:
                current = current * 100
            else:
                # nineteen eighty → 1980
                if val < 10 and current >= 20:
                    current = current * 10 + val
                else:
                    current += val

        elif w == "hundred":
            current *= 100

        elif w == "thousand":
            current *= 1000
            total += current
            current = 0

        elif w == "and":
            continue

    return str(total + current)

# 
NUM_PATTERN = r"(?:a|oh|zero|one|two|three|four|five|six|seven|eight|nine|ten|" \
              r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|" \
              r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|" \
              r"hundred|thousand|and|" \
              r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|" \
              r"eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|" \
              r"eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|" \
              r"seventieth|eightieth|ninetieth)" \
              r"(?:[- ](?:a|oh|zero|one|two|three|four|five|six|seven|eight|nine|ten|" \
              r"eleven|twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|" \
              r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|" \
              r"hundred|thousand|and|" \
              r"first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth|" \
              r"eleventh|twelfth|thirteenth|fourteenth|fifteenth|sixteenth|seventeenth|" \
              r"eighteenth|nineteenth|twentieth|thirtieth|fortieth|fiftieth|sixtieth|" \
              r"seventieth|eightieth|ninetieth))*"

# 
def word_to_number(text):
    def repl(match):
        phrase = match.group().replace("-", " ")
        words = phrase.split()
        return parse_number_phrase(words)

    return re.sub(NUM_PATTERN, repl, text)
