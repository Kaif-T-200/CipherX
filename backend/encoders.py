"""
Encoder functions for CipherX - Reverse operations of decoders
"""

import base64
from urllib.parse import quote
import json

def encode_base64(text):
    """Encode to Base64"""
    try:
        return base64.b64encode(text.encode()).decode()
    except:
        return None

def encode_base32(text):
    """Encode to Base32"""
    try:
        return base64.b32encode(text.encode()).decode()
    except:
        return None

def encode_hex(text):
    """Encode to Hexadecimal"""
    try:
        return text.encode().hex()
    except:
        return None

def encode_binary(text):
    """Encode to Binary"""
    try:
        return ' '.join(format(ord(c), '08b') for c in text)
    except:
        return None

def encode_url(text):
    """URL Encode"""
    try:
        return quote(text)
    except:
        return None

def encode_rot13(text):
    """ROT13 Encode"""
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + 13) % 26 + base)
        else:
            result += char
    return result

def encode_caesar(text, shift=3):
    """Caesar Cipher Encode"""
    result = ""
    for char in text:
        if char.isalpha():
            base = ord('A') if char.isupper() else ord('a')
            result += chr((ord(char) - base + shift) % 26 + base)
        else:
            result += char
    return result

def encode_atbash(text):
    """Atbash Cipher Encode"""
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

def encode_reverse(text):
    """Reverse String"""
    return text[::-1]

def encode_morse(text):
    """Morse Code Encode"""
    MORSE_CODE = {
        'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.',
        'F': '..-.', 'G': '--.', 'H': '....', 'I': '..', 'J': '.---',
        'K': '-.-', 'L': '.-..', 'M': '--', 'N': '-.', 'O': '---',
        'P': '.--.', 'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
        'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 'Y': '-.--',
        'Z': '--..', ' ': '/',
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.'
    }
    
    result = []
    for char in text.upper():
        if char in MORSE_CODE:
            result.append(MORSE_CODE[char])
    
    return ' '.join(result)

def encode_unicode_escape(text):
    """Unicode Escape Encode"""
    return text.encode('unicode_escape').decode()

def encode_xor(text, key=0x42):
    """XOR Encode with key"""
    try:
        result = ''.join(chr(ord(c) ^ key) for c in text)
        return result.encode('unicode_escape').decode()
    except:
        return None
