from urllib.parse import unquote, quote

def decode_url(text):
    """URL decode"""
    try:
        decoded = unquote(text)
        if decoded != text:  # Only return if actually decoded something
            return [decoded]
    except:
        pass
    return []

def encode_url(text):
    """URL encode"""
    try:
        return [quote(text)]
    except:
        return []
