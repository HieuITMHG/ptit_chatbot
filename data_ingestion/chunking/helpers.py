import tiktoken

encoding = tiktoken.encoding_for_model("gpt-5-nano")

def length_function(text: str) -> int:
    encoded = encoding.encode(text)
    return encoded, len(encoded)