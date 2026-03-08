import base64
import re

def decode_base64(text):
    try:
        # Clean the string of any characters not in the Base64 alphabet
        # This handles challenges where Base64 is padded or split with noise characters
        clean_text = re.sub(r'[^A-Za-z0-9+/=_-]', '', text)
        
        # Handle URL-safe base64 by normalizing back to standard
        clean_text = clean_text.replace('-', '+').replace('_', '/')
        
        # Add padding if missing
        missing_padding = len(clean_text) % 4
        if missing_padding:
            clean_text += '=' * (4 - missing_padding)
            
        decoded = base64.b64decode(clean_text).decode('utf-8')
        return [decoded]
    except:
        # Fallback to bytes if utf-8 fails, but return list of printable only
        try:
            # Re-clean strictly for bytes
            strict_clean = re.sub(r'[^A-Za-z0-9+/=_-]', '', text).replace('-', '+').replace('_', '/')
            missing_padding = len(strict_clean) % 4
            if missing_padding:
                strict_clean += '=' * (4 - missing_padding)
            raw = base64.b64decode(strict_clean)
            if all(32 <= b <= 126 or b in [10, 13] for b in raw):
                return [raw.decode('latin-1')]
        except:
            pass
        return []