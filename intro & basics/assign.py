## Problem: make your own tokenizer

alphabets = [
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
]

uppercase_alphabets = [letter.upper() for letter in alphabets]

count = 0

tokenizer = {}

for letter in alphabets:
    count += 1
    tokenizer[letter] = count

for letter in uppercase_alphabets:
    count += 1
    tokenizer[letter] = count

tokenizer[" "] = 101

print("Tokenizer Dict =>", tokenizer)


def tokenize(text):
    tokens = []
    for char in text:
        tokens.append(tokenizer.get(char, "UNKNOWN"))
    return tokens


tokenized_result_1 = tokenize("My name is Anshul Kardam")

tokenized_result_2 = tokenize("I do Backend & Frontend Both")

tokenized_result_3 = tokenize("8 * 8 is 64")

print("tokenized_result_1 =>", tokenized_result_1)
print("tokenized_result_2 =>", tokenized_result_2)
print("tokenized_result_3 =>", tokenized_result_3)


def detokenize(tokens):
    print("tokenizer.items() =>", tokenizer.items())
    # Here we are creating a new dictionary by reversing the original tokenizer.
    # tokenizer.items() gives pairs like ("a", 1), ("b", 2)
    # The loop `for letter, count in tokenizer.items()` takes each pair
    # and assigns "letter" = "a", "count" = 1, etc.
    # Then we build {count: letter}, so 1 maps to "a", 2 maps to "b".
    reverse_tokenizer = {count: letter for letter, count in tokenizer.items()}
    print("reverse tokenizer result =>", reverse_tokenizer)
    return "".join(reverse_tokenizer.get(t, "?") for t in tokens)


random_tokens = detokenize([1, 28, 98, 34, 90, 3])

detokenized_result_1 = detokenize(
    [
        39,
        25,
        101,
        14,
        1,
        13,
        5,
        101,
        9,
        19,
        101,
        27,
        14,
        19,
        8,
        21,
        12,
        101,
        37,
        1,
        18,
        4,
        1,
        13,
    ]
)

print("random_tokens detokenized =>", random_tokens)


print("result of tokenized_1 detokenized =>", detokenized_result_1)
