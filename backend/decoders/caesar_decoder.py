def decode_caesar(text):
    """
    Decode Caesar cipher by trying all 25 possible shifts.
    Returns each shift as a SEPARATE result for AI validation.
    """
    results = []
    for shift in range(1, 26):
        decoded = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                decoded += chr((ord(char) - base - shift) % 26 + base)
            else:
                decoded += char
        # Return each shift individually (not all in one string!)
        results.append(decoded)
    return results