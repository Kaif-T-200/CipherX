def decode_binary(text):
    try:
        # Safety check: don't process huge binary strings
        if len(text) > 200000:
            return []

        compact = ''.join(ch for ch in text if ch in '01')

        # Must be pure binary and full bytes
        if len(compact) < 8 or len(compact) % 8 != 0:
            return []

        # Decode in 8-bit chunks regardless of source spacing
        decoded = ''.join(chr(int(compact[i:i + 8], 2)) for i in range(0, len(compact), 8))
        return [decoded] if decoded and len(decoded) < 10000 else []
    except:
        return []