def decode_hex(text):
    try:
        # Smart cleanup: remove spaces, newlines, colons, dashes, and common separators
        cleaned = text.replace(' ', '').replace('\n', '').replace('\r', '')
        cleaned = cleaned.replace(':', '').replace('-', '').replace('\\x', '')
        cleaned = cleaned.replace('0x', '')  # Remove 0x prefix if present
        
        # Ensure even length for valid hex
        if len(cleaned) % 2 != 0:
            return []
        
        decoded = bytes.fromhex(cleaned).decode('utf-8', errors='ignore')
        
        # Only return if we got meaningful output
        if decoded and len(decoded.strip()) > 0:
            return [decoded]
        return []
    except:
        return []