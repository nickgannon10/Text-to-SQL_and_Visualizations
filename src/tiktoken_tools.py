def num_tokens_from_string(string: str, encoding_name: str) -> int:
    import tiktoken
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def clip_tokens(string: str, encoding_name: str, max_tokens: int) -> str:
    import tiktoken
    """Clips the string to not exceed the max_tokens limit."""
    # Get the encoding object
    encoding = tiktoken.get_encoding(encoding_name)
    # Encode the string into tokens
    tokens = encoding.encode(string)
    # Check if the number of tokens exceeds max_tokens
    if len(tokens) > max_tokens:
        # If so, truncate the token list to the first max_tokens tokens
        tokens = tokens[:max_tokens]
    # Decode the truncated list of tokens back into a string
    clipped_string = encoding.decode(tokens)
    return clipped_string