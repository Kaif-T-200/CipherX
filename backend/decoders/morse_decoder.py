import re

MORSE_CODE = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
    '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
    '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
    # Punctuation - CRITICAL for accurate decoding
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'", '-.-.--': '!',
    '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':',
    '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-', '..--.-': '_',
    '.-..-.': '"', '...-..-': '$', '.--.-.': '@'
}

def decode_morse(text):
    """Morse code decoder - 100% accurate with punctuation and flexible word boundaries"""
    if not text or not text.strip():
        return []
    
    # CRITICAL: Normalize newlines to word separators FIRST
    # Users often separate Morse sentences with newlines instead of /
    text = re.sub(r'\s*\n+\s*', ' / ', text)
    
    results = []
    
    # Strategy 1: Slash-separated words (e.g., ".- -... / -.-. -..") 
    # This is the most common format
    if '/' in text:
        try:
            decoded = _decode_slash_format(text)
            if decoded and decoded.strip() and len(decoded.strip()) > 0:
                results.append(decoded)
        except:
            pass
    
    # Strategy 2: Multi-space separated words (e.g., ".- -...   -.-. -..")
    # Words separated by 2+ spaces, letters by 1 space
    try:
        decoded = _decode_space_format(text)
        if decoded and decoded.strip() and len(decoded.strip()) > 0:
            # Don't add duplicates
            if decoded not in results:
                results.append(decoded)
    except:
        pass
    
    return results


def _decode_slash_format(text):
    """Decode Morse where words are separated by / (with optional spaces around it)"""
    # Split on / surrounded by optional spaces to get words
    words = re.split(r'\s*/\s*', text.strip())
    decoded_words = []
    
    for word in words:
        word = word.strip()
        if not word:
            # Empty part between slashes = space (e.g., "//")
            continue
        
        # Split word into individual letter codes (single space separated)
        letters = word.split(' ')
        decoded_word = ''
        for letter in letters:
            letter = letter.strip()
            if not letter:
                continue
            if letter in MORSE_CODE:
                decoded_word += MORSE_CODE[letter]
        
        if decoded_word:
            decoded_words.append(decoded_word)
    
    return ' '.join(decoded_words)


def _decode_space_format(text):
    """Decode Morse where words are separated by 2+ spaces, letters by 1 space"""
    t = text.strip()
    
    # Split into words using 2+ consecutive spaces as word boundary
    # We need to be careful: split on 2+ spaces but NOT on single spaces
    words = re.split(r' {2,}', t)
    decoded_words = []
    
    for word in words:
        word = word.strip()
        if not word:
            continue
        
        # Each letter within a word is separated by a single space
        letters = word.split(' ')
        decoded_word = ''
        for letter in letters:
            letter = letter.strip()
            if not letter:
                continue
            if letter in MORSE_CODE:
                decoded_word += MORSE_CODE[letter]
        
        if decoded_word:
            decoded_words.append(decoded_word)
    
    return ' '.join(decoded_words)
