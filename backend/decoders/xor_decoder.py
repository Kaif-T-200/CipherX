def decode_xor(text):
    results = []
    try:
        raw = text.encode()
        for key in range(1, 256):
            decoded = ''.join(chr(b ^ key) for b in raw)
            results.append(decoded)
    except:
        pass
    return results[:20]