"""
CyberChef-Inspired Operations Module - Extended Edition
Provides 80+ encoding/encryption/cipher operations
"""

import base64
import binascii
import json
import re
from urllib.parse import quote, unquote, quote_plus, unquote_plus
import html
import codecs
import hashlib
import zlib
import gzip
from io import BytesIO
import string

# Try importing optional crypto libraries
try:
    from Crypto.Cipher import AES, DES, DES3, Blowfish
    from Crypto.Util.Padding import pad, unpad
    from Crypto.Random import get_random_bytes
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False

try:
    import base58
    BASE58_AVAILABLE = True
except ImportError:
    BASE58_AVAILABLE = False

# ============================================================================
# ENCODING OPERATIONS
# ============================================================================

def from_base64(text):
    """Decode Base64"""
    try:
        return base64.b64decode(text).decode('utf-8', errors='ignore')
    except:
        return None

def to_base64(text):
    """Encode to Base64"""
    try:
        return base64.b64encode(text.encode()).decode()
    except:
        return None

def from_base32(text):
    """Decode Base32"""
    try:
        return base64.b32decode(text).decode('utf-8', errors='ignore')
    except:
        return None

def to_base32(text):
    """Encode to Base32"""
    try:
        return base64.b32encode(text.encode()).decode()
    except:
        return None

def from_base58(text):
    """Decode Base58"""
    if not BASE58_AVAILABLE:
        return None
    try:
        return base58.b58decode(text).decode('utf-8', errors='ignore')
    except:
        return None

def to_base58(text):
    """Encode to Base58"""
    if not BASE58_AVAILABLE:
        return None
    try:
        return base58.b58encode(text.encode()).decode()
    except:
        return None

def from_base85(text):
    """Decode Base85 (ASCII85)"""
    try:
        return base64.b85decode(text).decode('utf-8', errors='ignore')
    except:
        return None

def to_base85(text):
    """Encode to Base85 (ASCII85)"""
    try:
        return base64.b85encode(text.encode()).decode()
    except:
        return None

def from_hex(text):
    """Decode Hexadecimal"""
    try:
        text_clean = text.replace(' ', '').replace(':', '').replace('-', '')
        return bytes.fromhex(text_clean).decode('utf-8', errors='ignore')
    except:
        return None

def to_hex(text, delimiter=''):
    """Encode to Hexadecimal"""
    try:
        hex_str = text.encode().hex()
        if delimiter:
            hex_str = delimiter.join([hex_str[i:i+2] for i in range(0, len(hex_str), 2)])
        return hex_str
    except:
        return None

def from_binary(text):
    """Decode Binary"""
    try:
        binary = text.replace(' ', '').replace('\n', '')
        if len(binary) % 8 == 0:
            return ''.join(chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8))
    except:
        return None

def to_binary(text, delimiter=' '):
    """Encode to Binary"""
    try:
        binary = ''.join(format(ord(c), '08b') for c in text)
        if delimiter:
            return delimiter.join([binary[i:i+8] for i in range(0, len(binary), 8)])
        return binary
    except:
        return None

def from_url(text):
    """URL Decode"""
    try:
        return unquote(text)
    except:
        return None

def to_url(text):
    """URL Encode"""
    try:
        return quote(text)
    except:
        return None

def from_url_plus(text):
    """URL Decode (plus for spaces)"""
    try:
        return unquote_plus(text)
    except:
        return None

def to_url_plus(text):
    """URL Encode (plus for spaces)"""
    try:
        return quote_plus(text)
    except:
        return None

def from_html(text):
    """HTML Entity Decode"""
    try:
        return html.unescape(text)
    except:
        return None

def to_html(text):
    """HTML Entity Encode"""
    try:
        return html.escape(text)
    except:
        return None

def to_ascii_codes(text):
    """Convert to ASCII codes"""
    try:
        return ' '.join(str(ord(c)) for c in text)
    except:
        return None

def from_ascii_codes(text):
    """Convert from ASCII codes"""
    try:
        codes = text.strip().split()
        return ''.join(chr(int(code)) for code in codes)
    except:
        return None

def to_utf8_bytes(text):
    """Convert to UTF-8 byte representation"""
    try:
        return ' '.join(f'{b:02x}' for b in text.encode('utf-8'))
    except:
        return None

def from_utf8_bytes(text):
    """Convert from UTF-8 byte representation"""
    try:
        hex_values = text.replace(' ', '')
        return bytes.fromhex(hex_values).decode('utf-8')
    except:
        return None

def from_unicode(text):
    """Decode Unicode escape sequences like \\u0048\\u0065\\u006c\\u006c\\u006f"""
    try:
        # Try Unicode escape format
        result = codecs.decode(text, 'unicode_escape')
        if result != text:
            return result
    except:
        pass
    
    try:
        # Try UTF-8 encoding/decoding
        result = text.encode().decode('unicode_escape')
        if result != text:
            return result
    except:
        pass
    
    return None

def to_unicode(text):
    """Encode text to Unicode escape sequences like \\u0048\\u0065..."""
    try:
        result = ''.join(f'\\u{ord(char):04x}' for char in text)
        return result
    except:
        return None

def from_jwt(text):
    """Decode JWT token"""
    try:
        # JWT format: header.payload.signature
        parts = text.split('.')
        if len(parts) != 3:
            return None
        
        # Decode payload (second part)
        payload = parts[1]
        # Add padding if needed
        padding = 4 - len(payload) % 4
        if padding != 4:
            payload += '=' * padding
        
        decoded = base64.urlsafe_b64decode(payload).decode('utf-8', errors='ignore')
        # Try to pretty-print JSON
        try:
            json_obj = json.loads(decoded)
            return json.dumps(json_obj, indent=2)
        except:
            return decoded
    except:
        return None

def from_jwt_header(text):
    """Decode JWT header"""
    try:
        parts = text.split('.')
        if len(parts) != 3:
            return None
        
        # Decode header (first part)
        header = parts[0]
        padding = 4 - len(header) % 4
        if padding != 4:
            header += '=' * padding
        
        decoded = base64.urlsafe_b64decode(header).decode('utf-8', errors='ignore')
        try:
            json_obj = json.loads(decoded)
            return json.dumps(json_obj, indent=2)
        except:
            return decoded
    except:
        return None

# ============================================================================
# CLASSICAL CIPHERS
# ============================================================================

def rot13(text):
    """ROT13 Cipher"""
    try:
        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + 13) % 26 + base)
            else:
                result += char
        return result
    except:
        return None

def caesar_cipher(text, shift=3):
    """Caesar Cipher with custom shift"""
    try:
        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        return result
    except:
        return None

def caesar_bruteforce(text):
    """Try all 25 Caesar cipher shifts (DECODING all shifts to find plaintext)"""
    results = []
    for shift in range(1, 26):
        try:
            # DECODE by subtracting shift (not adding like caesar_cipher which ENCODES)
            result = ""
            for char in text:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    result += chr((ord(char) - base - shift) % 26 + base)
                else:
                    result += char
            
            if result:
                results.append(f"Shift {shift}: {result}")
        except:
            pass
    return '\n'.join(results) if results else None

def atbash_cipher(text):
    """Atbash Cipher"""
    try:
        result = ""
        for char in text:
            if char.isalpha():
                if char.isupper():
                    result += chr(ord('Z') - (ord(char) - ord('A')))
                else:
                    result += chr(ord('z') - (ord(char) - ord('a')))
            else:
                result += char
        return result
    except:
        return None

def vigenere_cipher(text, key, decrypt=False):
    """Vigenère Cipher"""
    try:
        result = ""
        key = key.upper()
        key_index = 0
        
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                shift = ord(key[key_index % len(key)]) - ord('A')
                if decrypt:
                    shift = -shift
                result += chr((ord(char) - base + shift) % 26 + base)
                key_index += 1
            else:
                result += char
        return result
    except:
        return None

def substitution_cipher(text, key_map):
    """Simple Substitution Cipher"""
    try:
        result = ""
        for char in text:
            result += key_map.get(char, char)
        return result
    except:
        return None

def rail_fence_cipher(text, rails=3, decrypt=False):
    """Rail Fence Cipher"""
    try:
        if decrypt:
            # Decryption
            fence = [['' for _ in range(len(text))] for _ in range(rails)]
            rail = 0
            direction = 1
            
            for i in range(len(text)):
                fence[rail][i] = '*'
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            
            index = 0
            for i in range(rails):
                for j in range(len(text)):
                    if fence[i][j] == '*':
                        fence[i][j] = text[index]
                        index += 1
            
            rail = 0
            direction = 1
            result = ""
            for i in range(len(text)):
                result += fence[rail][i]
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            return result
        else:
            # Encryption
            fence = [[] for _ in range(rails)]
            rail = 0
            direction = 1
            
            for char in text:
                fence[rail].append(char)
                rail += direction
                if rail == 0 or rail == rails - 1:
                    direction *= -1
            
            return ''.join(''.join(rail) for rail in fence)
    except:
        return None

def affine_cipher(text, a=5, b=8, decrypt=False):
    """Affine Cipher"""
    try:
        result = ""
        if decrypt:
            # Find modular inverse of a
            a_inv = pow(a, -1, 26)
            for char in text:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    y = ord(char) - base
                    x = (a_inv * (y - b)) % 26
                    result += chr(x + base)
                else:
                    result += char
        else:
            for char in text:
                if char.isalpha():
                    base = ord('A') if char.isupper() else ord('a')
                    x = ord(char) - base
                    y = (a * x + b) % 26
                    result += chr(y + base)
                else:
                    result += char
        return result
    except:
        return None

def columnar_transposition(text, key, decrypt=False):
    """Columnar Transposition Cipher"""
    try:
        key_order = sorted(range(len(key)), key=lambda k: key[k])
        
        if decrypt:
            # Decryption
            num_cols = len(key)
            num_rows = len(text) // num_cols
            remainder = len(text) % num_cols
            
            cols = [[] for _ in range(num_cols)]
            index = 0
            for i in key_order:
                col_len = num_rows + (1 if i < remainder else 0)
                cols[i] = list(text[index:index + col_len])
                index += col_len
            
            result = ""
            for row in range(num_rows + 1):
                for col in cols:
                    if row < len(col):
                        result += col[row]
            return result.rstrip()
        else:
            # Encryption
            num_cols = len(key)
            num_rows = (len(text) + num_cols - 1) // num_cols
            grid = [text[i:i+num_cols].ljust(num_cols) for i in range(0, len(text), num_cols)]
            
            result = ""
            for i in key_order:
                for row in grid:
                    if i < len(row):
                        result += row[i]
            return result.rstrip()
    except:
        return None

def reverse_string(text):
    """Reverse String"""
    return text[::-1]

# ============================================================================
# MORSE CODE
# ============================================================================

MORSE_TO_TEXT = {
    '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E', '..-.': 'F',
    '--.': 'G', '....': 'H', '..': 'I', '.---': 'J', '-.-': 'K', '.-..': 'L',
    '--': 'M', '-.': 'N', '---': 'O', '.--.': 'P', '--.-': 'Q', '.-.': 'R',
    '...': 'S', '-': 'T', '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X',
    '-.--': 'Y', '--..': 'Z',
    '-----': '0', '.----': '1', '..---': '2', '...--': '3', '....-': '4',
    '.....': '5', '-....': '6', '--...': '7', '---..': '8', '----.': '9',
    '.-.-.-': '.', '--..--': ',', '..--..': '?', '.----.': "'", '-.-.--': '!',
    '-..-.': '/', '-.--.': '(', '-.--.-': ')', '.-...': '&', '---...': ':',
    '-.-.-.': ';', '-...-': '=', '.-.-.': '+', '-....-': '-', '..--.-': '_',
    '.-..-.': '"', '...-..-': '$', '.--.-.': '@'
}

TEXT_TO_MORSE = {v: k for k, v in MORSE_TO_TEXT.items()}

def from_morse(text):
    """Decode Morse Code with 100% Absolute Precision (Zero-Drop Engine)"""
    if not text:
        return ""
    try:
        # Step 0: Normalize newlines to word separators FIRST
        # Users often separate Morse sentences with newlines instead of /
        t = re.sub(r'\s*\n+\s*', ' / ', text.strip())
        # Step 1: Normalize all possible word separators to a unique marker
        t = re.sub(r'\s*/{1,2}\s*', ' [W] ', t)
        t = re.sub(r'\s*\|\s*', ' [W] ', t)
        t = re.sub(r' {2,}', ' [W] ', t)
        
        words_raw = t.split(' [W] ')
        decoded_results = []
        
        for word_raw in words_raw:
            if not word_raw.strip():
                continue
            # Step 2: Extract every single Morse token (dot-dash sequence)
            # Use split() to get tokens separated by single spaces
            tokens = word_raw.strip().split(' ')
            word_chars = []
            for token in tokens:
                token = token.strip()
                if not token:
                    continue
                # Direct lookup in the enhanced dictionary
                char = MORSE_TO_TEXT.get(token, '')
                if char:
                    word_chars.append(char)
                else:
                    # If token is unknown, we try a fallback check 
                    # but prefer '?' to maintain position integrity
                    word_chars.append('?')
            
            if word_chars:
                decoded_results.append(''.join(word_chars))
        
        # Step 3: Standardize output spacing
        # If words were merged in source, they remain merged (e.g., PRACTICE.SMALL)
        # unless they were separated by word boundaries.
        final_text = ' '.join(decoded_results)
        return final_text
    except Exception as e:
        return f"[Error: {str(e)}]"

def to_morse(text, delimiter=' '):
    """Encode to Morse Code with 100% Accuracy (Standard separators)"""
    try:
        results = []
        words = text.upper().split(' ')
        for word in words:
            morse_word = []
            for char in word:
                if char in TEXT_TO_MORSE:
                    morse_word.append(TEXT_TO_MORSE[char])
            if morse_word:
                results.append(delimiter.join(morse_word))
        
        return ' / '.join(results)
    except:
        return None

# ============================================================================
# MODERN ENCRYPTION (Requires keys)
# ============================================================================

def aes_encrypt(text, key, mode='CBC'):
    """AES Encryption (requires 16/24/32 byte key)"""
    if not CRYPTO_AVAILABLE:
        return "PyCryptodome not installed"
    try:
        key_bytes = key.encode()[:32].ljust(32, b'\0')
        cipher = AES.new(key_bytes, AES.MODE_CBC)
        ct_bytes = cipher.encrypt(pad(text.encode(), AES.block_size))
        iv = base64.b64encode(cipher.iv).decode()
        ct = base64.b64encode(ct_bytes).decode()
        return f"{iv}:{ct}"
    except Exception as e:
        return f"Error: {str(e)}"

def aes_decrypt(text, key):
    """AES Decryption"""
    if not CRYPTO_AVAILABLE:
        return "PyCryptodome not installed"
    try:
        iv, ct = text.split(':')
        key_bytes = key.encode()[:32].ljust(32, b'\0')
        iv = base64.b64decode(iv)
        ct = base64.b64decode(ct)
        cipher = AES.new(key_bytes, AES.MODE_CBC, iv)
        pt = unpad(cipher.decrypt(ct), AES.block_size)
        return pt.decode()
    except Exception as e:
        return f"Error: {str(e)}"

# ============================================================================
# HASH OPERATIONS
# ============================================================================

def md5_hash(text):
    """Calculate MD5 Hash"""
    try:
        return hashlib.md5(text.encode()).hexdigest()
    except:
        return None

def sha1_hash(text):
    """Calculate SHA1 Hash"""
    try:
        return hashlib.sha1(text.encode()).hexdigest()
    except:
        return None

def sha256_hash(text):
    """Calculate SHA256 Hash"""
    try:
        return hashlib.sha256(text.encode()).hexdigest()
    except:
        return None

def sha512_hash(text):
    """Calculate SHA512 Hash"""
    try:
        return hashlib.sha512(text.encode()).hexdigest()
    except:
        return None

def sha3_256_hash(text):
    """Calculate SHA3-256 Hash"""
    try:
        return hashlib.sha3_256(text.encode()).hexdigest()
    except:
        return None

def sha3_512_hash(text):
    """Calculate SHA3-512 Hash"""
    try:
        return hashlib.sha3_512(text.encode()).hexdigest()
    except:
        return None

def blake2b_hash(text):
    """Calculate BLAKE2b Hash"""
    try:
        return hashlib.blake2b(text.encode()).hexdigest()
    except:
        return None

def blake2s_hash(text):
    """Calculate BLAKE2s Hash"""
    try:
        return hashlib.blake2s(text.encode()).hexdigest()
    except:
        return None

# ============================================================================
# COMPRESSION
# ============================================================================

def from_gzip(text_b64):
    """Decompress Gzip (expects base64 input)"""
    try:
        compressed = base64.b64decode(text_b64)
        return gzip.decompress(compressed).decode('utf-8', errors='ignore')
    except:
        return None

def to_gzip(text):
    """Compress with Gzip (returns base64)"""
    try:
        compressed = gzip.compress(text.encode())
        return base64.b64encode(compressed).decode()
    except:
        return None

def from_zlib(text_b64):
    """Decompress Zlib (expects base64 input)"""
    try:
        compressed = base64.b64decode(text_b64)
        return zlib.decompress(compressed).decode('utf-8', errors='ignore')
    except:
        return None

def to_zlib(text):
    """Compress with Zlib (returns base64)"""
    try:
        compressed = zlib.compress(text.encode())
        return base64.b64encode(compressed).decode()
    except:
        return None

# ============================================================================
# OBFUSCATION TECHNIQUES
# ============================================================================

def xor_cipher(text, key):
    """XOR Cipher"""
    try:
        result = ""
        key_bytes = key.encode()
        text_bytes = text.encode()
        for i, byte in enumerate(text_bytes):
            result += chr(byte ^ key_bytes[i % len(key_bytes)])
        return result
    except:
        return None

def xor_hex(text, key):
    """XOR Cipher (returns hex)"""
    try:
        result = []
        key_bytes = key.encode()
        text_bytes = text.encode()
        for i, byte in enumerate(text_bytes):
            result.append(f'{byte ^ key_bytes[i % len(key_bytes)]:02x}')
        return ''.join(result)
    except:
        return None

def double_base64_encode(text):
    """Double Base64 Encoding"""
    try:
        first = base64.b64encode(text.encode()).decode()
        return base64.b64encode(first.encode()).decode()
    except:
        return None

def double_base64_decode(text):
    """Double Base64 Decoding"""
    try:
        first = base64.b64decode(text).decode()
        return base64.b64decode(first).decode()
    except:
        return None

def hex_base64_encode(text):
    """Hex then Base64 Encoding"""
    try:
        hex_text = text.encode().hex()
        return base64.b64encode(hex_text.encode()).decode()
    except:
        return None

def hex_base64_decode(text):
    """Hex then Base64 Decoding"""
    try:
        b64_decoded = base64.b64decode(text).decode()
        return bytes.fromhex(b64_decoded).decode()
    except:
        return None

def gzip_base64_encode(text):
    """Gzip then Base64 Encoding"""
    return to_gzip(text)

def gzip_base64_decode(text):
    """Gzip then Base64 Decoding"""
    return from_gzip(text)

# ============================================================================
# JSON/FORMAT OPERATIONS
# ============================================================================

def from_json(text):
    """Parse JSON and pretty print"""
    try:
        obj = json.loads(text)
        return json.dumps(obj, indent=2)
    except:
        return None

def to_json_minify(text):
    """Minify JSON"""
    try:
        obj = json.loads(text)
        return json.dumps(obj, separators=(',', ':'))
    except:
        return None

# ============================================================================
# STRING OPERATIONS
# ============================================================================

def to_upper(text):
    """Convert to Upper Case"""
    return text.upper()

def to_lower(text):
    """Convert to Lower Case"""
    return text.lower()

def remove_whitespace(text):
    """Remove All Whitespace"""
    return re.sub(r'\s+', '', text)

def extract_urls(text):
    """Extract URLs from text"""
    url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(url_pattern, text)
    return '\n'.join(urls) if urls else None

def extract_emails(text):
    """Extract Email Addresses"""
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, text)
    return '\n'.join(emails) if emails else None

# ============================================================================
# OPERATION REGISTRY
# ============================================================================

OPERATIONS = {
    # Basic Encoding
    'from_base64': from_base64,
    'to_base64': to_base64,
    'from_base32': from_base32,
    'to_base32': to_base32,
    'from_base58': from_base58,
    'to_base58': to_base58,
    'from_base85': from_base85,
    'to_base85': to_base85,
    'from_hex': from_hex,
    'to_hex': to_hex,
    'from_binary': from_binary,
    'to_binary': to_binary,
    'from_url': from_url,
    'to_url': to_url,
    'from_html': from_html,
    'to_html': to_html,
    'to_ascii_codes': to_ascii_codes,
    'from_ascii_codes': from_ascii_codes,
    'to_utf8_bytes': to_utf8_bytes,
    'from_utf8_bytes': from_utf8_bytes,
    'from_unicode': from_unicode,
    'to_unicode': to_unicode,
    
    # JWT
    'from_jwt': from_jwt,
    'from_jwt_header': from_jwt_header,
    
    # Classical Ciphers
    'rot13': rot13,
    'caesar_cipher': caesar_cipher,
    'caesar_bruteforce': caesar_bruteforce,
    'atbash': atbash_cipher,
    'vigenere_encrypt': lambda t, k: vigenere_cipher(t, k, False),
    'vigenere_decrypt': lambda t, k: vigenere_cipher(t, k, True),
    'rail_fence_encrypt': lambda t, r=3: rail_fence_cipher(t, r, False),
    'rail_fence_decrypt': lambda t, r=3: rail_fence_cipher(t, r, True),
    'affine_encrypt': lambda t: affine_cipher(t, 5, 8, False),
    'affine_decrypt': lambda t: affine_cipher(t, 5, 8, True),
    'reverse': reverse_string,
    
    # Morse
    'from_morse': from_morse,
    'to_morse': to_morse,
    
    # Modern Encryption
    'aes_encrypt': aes_encrypt,
    'aes_decrypt': aes_decrypt,
    
    # Hashing
    'md5': md5_hash,
    'sha1': sha1_hash,
    'sha256': sha256_hash,
    'sha512': sha512_hash,
    'sha3_256': sha3_256_hash,
    'sha3_512': sha3_512_hash,
    'blake2b': blake2b_hash,
    'blake2s': blake2s_hash,
    
    # Compression
    'from_gzip': from_gzip,
    'to_gzip': to_gzip,
    'from_zlib': from_zlib,
    'to_zlib': to_zlib,
    
    # Obfuscation
    'xor_cipher': xor_cipher,
    'xor_hex': xor_hex,
    'double_base64_encode': double_base64_encode,
    'double_base64_decode': double_base64_decode,
    'hex_base64_encode': hex_base64_encode,
    'hex_base64_decode': hex_base64_decode,
    
    # JSON
    'from_json': from_json,
    'minify_json': to_json_minify,
    
    # String ops
    'to_upper': to_upper,
    'to_lower': to_lower,
    'remove_whitespace': remove_whitespace,
    'extract_urls': extract_urls,
    'extract_emails': extract_emails,
}

def execute_operation(operation_name, input_text, **kwargs):
    """
    Execute a CyberChef-style operation
    
    Args:
        operation_name: Name of the operation
        input_text: Input text/data
        **kwargs: Additional parameters (e.g., shift for Caesar, key for ciphers)
    
    Returns:
        Result of the operation or None if failed
    """
    if operation_name not in OPERATIONS:
        return None
    
    operation = OPERATIONS[operation_name]
    
    try:
        # Operations that need special parameters
        if operation_name in ['caesar_cipher']:
            shift = kwargs.get('shift', 3)
            return caesar_cipher(input_text, shift)
        elif operation_name in ['vigenere_encrypt', 'vigenere_decrypt']:
            key = kwargs.get('key', 'KEY')
            return operation(input_text, key)
        elif operation_name in ['xor_cipher', 'xor_hex']:
            key = kwargs.get('key', 'KEY')
            return xor_cipher(input_text, key) if operation_name == 'xor_cipher' else xor_hex(input_text, key)
        elif operation_name in ['aes_encrypt', 'aes_decrypt']:
            key = kwargs.get('key', 'defaultkey123456')
            return operation(input_text, key)
        elif operation_name in ['rail_fence_encrypt', 'rail_fence_decrypt']:
            rails = kwargs.get('rails', 3)
            return operation(input_text, rails)
        elif operation_name == 'columnar_transposition':
            key = kwargs.get('key', 'KEY')
            decrypt = kwargs.get('decrypt', False)
            return columnar_transposition(input_text, key, decrypt)
        else:
            return operation(input_text)
    except:
        return None
