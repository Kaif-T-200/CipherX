def decode_rot13(text):
    """ROT13 decoder - special case of Caesar with 13 shift"""
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + 13) % 26 + base)
        else:
            result += char
    return [result] if result else []
