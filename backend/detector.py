import re

def _is_likely_reversed(text):
    """Check if text is likely reversed by comparing common English patterns"""
    if not text or len(text) < 4:
        return False
    
    reversed_text = text[::-1].lower()
    original_lower = text.lower()
    
    # Common English word patterns that should appear at the start
    common_starts = ["the ", "this ", "that ", "hello", "flag", "ctf", "test", "here"]
    common_ends = [" world", " test", " flag"]
    
    # Check if reversed version has common English starts
    for start in common_starts:
        if reversed_text.startswith(start):
            return True
    
    # Check if original has common English endings (meaning it's reversed)
    for end in common_ends:
        if original_lower.startswith(end[::-1]):  # reversed ending at start
            return True
    
    return False

def _alpha_ratio(text):
    """Return alphabetic character ratio for heuristic text checks."""
    if not text:
        return 0.0
    alpha = sum(1 for c in text if c.isalpha())
    return alpha / max(len(text), 1)

def _is_likely_classical_cipher_text(text):
    """Heuristic for text that is likely Caesar/ROT/Atbash-style content."""
    if not text:
        return False

    # Allow regular punctuation used in sentences; reject heavy symbol noise.
    allowed_pattern = r"[A-Za-z0-9\s,.;:!?\-_'\"()\[\]/{}]+"
    if not re.fullmatch(allowed_pattern, text):
        return False

    ratio = _alpha_ratio(text)
    return ratio >= 0.5

def detect_possible(text):
    """AI-powered detection of encoding types based on patterns - OPTIMIZED"""
    methods = []
    text_stripped = text.strip()
    text_len = len(text_stripped)
    
    if text_len == 0:
        return []
    
    # JWT detection (3 base64 parts separated by dots) - very specific
    if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', text_stripped):
        methods.append("jwt")
        return methods  # JWT is very specific, try it first
    
    # Morse code detection (dots, dashes, spaces, slashes) - check length
    if re.fullmatch(r'[\.\-\s/]+', text_stripped) and text_len > 5 and text_len < 10000:
        morse_count = text_stripped.count('.')
        dash_count = text_stripped.count('-')
        if morse_count >= 2 or dash_count >= 2:
            methods.append("morse")
    
    # URL encoded detection (contains %XX patterns) - very specific
    if re.search(r'%[0-9A-Fa-f]{2}', text):
        methods.append("url")
    
    # Unicode escape detection - specific patterns
    if re.search(r'\\u[0-9a-fA-F]{4}', text) or re.search(r'\\x[0-9a-fA-F]{2}', text):
        methods.append("unicode")
    
    # Base64 detection - allow URL-safe characters and some noise
    if re.search(r'[A-Za-z0-9+/=_-]{4,}', text_stripped):
        # Clean string to check length logic
        clean_b64 = re.sub(r'[^A-Za-z0-9+/=_]', '', text_stripped)
        if len(clean_b64) >= 4:
            methods.append("base64")
    
    # Base32 detection - tolerate whitespace/lowercase, then validate strictly
    text_compact = re.sub(r'\s+', '', text_stripped)
    text_base32 = text_compact.upper()
    if re.fullmatch(r'[A-Z2-7=]+', text_base32):
        if len(text_base32) % 8 == 0 and len(text_base32) >= 8:
            methods.append("base32")
    
    # Hex detection - tolerate separators often present in copied payloads
    text_hex = re.sub(r'[\s:\-]', '', text_stripped)
    if re.fullmatch(r'[0-9a-fA-F]+', text_hex):
        if len(text_hex) % 2 == 0 and len(text_hex) >= 4 and len(text_hex) < 200000:
            methods.append("hex")
    
    # Binary detection - tolerate any whitespace layout (spaces/newlines/tabs)
    text_binary = re.sub(r'\s+', '', text_stripped)
    if re.fullmatch(r'[01]+', text_binary):
        binary_len = len(text_binary)
        if binary_len % 8 == 0 and binary_len >= 8 and binary_len < 200000:
            methods.append("binary")
    
    likely_classical = _is_likely_classical_cipher_text(text_stripped)

    # ROT13/Caesar/Atbash for sentence-like text (including punctuation) and long paragraphs
    # PRIORITY ORDER: try shift ciphers FIRST before reverse for better detection
    if likely_classical and text_len >= 4 and text_len < 10000:
        # Classical ciphers should run before reverse for proper scoring
        methods.append("rot13")
        methods.append("caesar")
        methods.append("atbash")
        
        # Smart reversed text detection - only if text appears reversed
        if _is_likely_reversed(text_stripped):
            methods.insert(0, "reverse")  # High priority if detected
        else:
            # Add reverse as fallback at the end
            methods.append("reverse")
    else:
        # For non-classical text, try reverse
        methods.append("reverse")
    
    # XOR brute force is expensive and noisy; use as fallback, not primary path.
    strong_structured_match = any(m in methods for m in ["jwt", "morse", "url", "unicode", "base64", "base32", "hex", "binary"])
    if text_len < 1000 and (not strong_structured_match) and (not likely_classical):
        methods.append("xor")
    elif text_len < 180 and len(methods) <= 2:
        # Keep XOR available for short ambiguous payloads.
        methods.append("xor")
    
    return list(dict.fromkeys(methods))  # Remove duplicates while preserving order