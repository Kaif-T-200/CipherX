import re
import codecs

def decode_unicode_escape(text):
    """Decode Unicode escape sequences like \\u0048\\u0065\\u006c\\u006c\\u006f"""
    try:
        # Try standard unicode escape
        decoded = codecs.decode(text, 'unicode_escape')
        if decoded != text:
            return [decoded]
    except:
        pass
    
    # Try \u format
    try:
        decoded = text.encode().decode('unicode_escape')
        if decoded != text:
            return [decoded]
    except:
        pass
    
    return []
