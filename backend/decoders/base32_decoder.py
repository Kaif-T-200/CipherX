import base64

def decode_base32(text):
    """Base32 decoder"""
    try:
        # Remove whitespace
        text = text.replace(' ', '').replace('\n', '').replace('\r', '').upper()
        decoded = base64.b32decode(text).decode()
        return [decoded]
    except:
        return []
