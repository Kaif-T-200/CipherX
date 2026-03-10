from detector import detect_possible
from scorer import score_text
from ai_validator import validate_text_quality, filter_results
from decoders.base64_decoder import decode_base64
from decoders.base32_decoder import decode_base32
from decoders.hex_decoder import decode_hex
from decoders.binary_decoder import decode_binary
from decoders.caesar_decoder import decode_caesar
from decoders.atbash_decoder import decode_atbash
from decoders.xor_decoder import decode_xor
from decoders.rot13_decoder import decode_rot13
from decoders.url_decoder import decode_url
from decoders.reverse_decoder import decode_reverse
from decoders.jwt_decoder import decode_jwt
from decoders.unicode_decoder import decode_unicode_escape
from decoders.morse_decoder import decode_morse
import re

MAX_DEPTH = 5  # Increased for multi-layer encoding
AI_VALIDATION = True  # Enable AI-powered validation to filter garbage results

DETERMINISTIC_METHODS = {"base64", "base32", "hex", "binary", "url", "jwt", "unicode", "morse"}

def _alpha_ratio(text):
    if not text:
        return 0.0
    alpha = sum(1 for c in text if c.isalpha())
    return alpha / max(len(text), 1)

def _looks_like_encoding(text):
    """Check if text looks like it could be another layer of encoding - Lenient for layered CTF challenges"""
    if not text or len(text) < 3:
        return False
    
    text_stripped = text.strip()
    
    # Check for Base64 pattern (Lenient: allow - and _ and ignore padding rule for heuristic)
    if re.search(r'[A-Za-z0-9+/=_-]{4,}', text_stripped):
        return True
    
    # Check for Hex pattern
    if re.fullmatch(r'[0-9a-fA-F\s:-]+', text_stripped) and len(text_stripped) >= 4:
        return True
    
    # Check for Base32 pattern
    if re.fullmatch(r'[A-Z2-7=]+', text_stripped.upper()):
        return True
    
    # Check for URL encoding
    if re.search(r'%[0-9A-Fa-f]{2}', text):
        return True
    
    return False

def _is_strict_base64_like(text):
    """Strict check for full-string base64/base64url payloads."""
    if not text:
        return False
    t = text.strip()
    # Allow URL-safe variants and optional padding.
    if not re.fullmatch(r'[A-Za-z0-9+/=_-]+', t):
        return False
    # Typical base64 payload lengths are multiples of 4.
    return len(t) >= 8 and len(t) % 4 == 0


def _is_flag_like(text):
    if not text:
        return False
    return bool(re.match(r'^[A-Za-z]{3,10}\{[A-Za-z0-9_\-]+\}$', text.strip()))


def _dedupe_results(results):
    """Keep the best and simplest version of duplicate decoded outputs."""
    best_by_key = {}
    for result in results:
        key = (result.get("method"), result.get("decoded"))
        existing = best_by_key.get(key)
        if existing is None:
            best_by_key[key] = result
            continue

        existing_score = existing.get("score", 0)
        current_score = result.get("score", 0)
        existing_layer = existing.get("layer", 999)
        current_layer = result.get("layer", 999)

        if current_score > existing_score:
            best_by_key[key] = result
        elif current_score == existing_score and current_layer < existing_layer:
            best_by_key[key] = result

    deduped = list(best_by_key.values())
    deduped.sort(key=lambda x: (-x.get("score", 0), x.get("layer", 999), len(x.get("chain", ""))))
    return deduped

def run_cipherx(text, depth=0, path="", use_ai_filter=True, max_depth=None):
    """
    AI-powered recursive decoder with intelligent validation
    Now filters garbage results and only shows valid English/language text!
    """
    if max_depth is None:
        max_depth = MAX_DEPTH
        
    if depth > max_depth:
        return []
    
    if not text or len(text.strip()) == 0:
        return []
    
    # Skip if text is too long (avoid performance issues)
    if len(text) > 100000:
        return [{"method": "toolarge", "decoded": text, "score": 0, "layer": depth + 1, "chain": "Text too large"}]

    methods = detect_possible(text)
    results = []

    for method in methods:
        decoded_list = []

        try:
            if method == "base64":
                decoded_list = decode_base64(text)
            elif method == "base32":
                decoded_list = decode_base32(text)
            elif method == "hex":
                decoded_list = decode_hex(text)
            elif method == "binary":
                decoded_list = decode_binary(text)
            elif method == "caesar":
                decoded_list = decode_caesar(text)
            elif method == "atbash":
                decoded_list = decode_atbash(text)
            elif method == "rot13":
                decoded_list = decode_rot13(text)
            elif method == "url":
                decoded_list = decode_url(text)
            elif method == "reverse":
                decoded_list = decode_reverse(text)
            elif method == "jwt":
                decoded_list = decode_jwt(text)
            elif method == "unicode":
                decoded_list = decode_unicode_escape(text)
            elif method == "morse":
                decoded_list = decode_morse(text)
            elif method == "xor":
                decoded_list = decode_xor(text)
        except Exception as e:
            # Skip this method if it errors
            continue

        for decoded in decoded_list:
            # Skip if decoded is same as input (no actual decoding happened)
            if decoded == text or not decoded or len(decoded.strip()) == 0:
                continue
            
            # Skip extremely long outputs
            if len(decoded) > 100000:
                continue
            
            # AI VALIDATION: Check if result is valid English/language text
            if use_ai_filter and AI_VALIDATION:
                is_valid, confidence, reason = validate_text_quality(decoded)
                
                # Trust validator's is_valid flag - it handles adaptive thresholds for short texts
                # Also allow intermediate encodings (confidence 50+) for multi-layer decode
                if not is_valid and confidence < 50:
                    continue  # Skip garbage results
                
                # Use AI confidence as score
                s = confidence
            else:
                # Fallback to old scoring
                try:
                    s = score_text(decoded)
                except:
                    s = 0

            # Method-aware ranking to reduce XOR over-detection in auto mode.
            if method in DETERMINISTIC_METHODS:
                s += 8

            # CRITICAL: Boost classical ciphers with strong English scores
            if method in {"caesar", "rot13", "atbash"} and s >= 80:
                s = min(100, s + 10)  # Strong boost for perfect English in shift ciphers

            # Flag-aware ranking for Caesar/ROT/Atbash results.
            # Prefer standard CTF-like prefixes when ciphertext looks like a flag token.
            if method in {"caesar", "rot13", "atbash"} and _is_flag_like(decoded):
                upper_decoded = decoded.upper()
                if upper_decoded.startswith("CTF{") or upper_decoded.startswith("FLAG{"):
                    s = min(100, s + 20)
                else:
                    s = max(0, s - 10)
            
            # Demote reverse if it doesn't have very strong English
            if method == "reverse" and s < 75:
                s = max(0, s - 15)  # Penalty for weak reverse results

            # If input itself looks like strict base64 and reversing it still produces base64, skip.
            # Use _is_strict_base64_like only (not _looks_like_encoding which is too broad and
            # would falsely match plain English like "Hello World!").
            if method == "reverse":
                if _is_strict_base64_like(text) and _is_strict_base64_like(decoded):
                    continue

            if method == "xor":
                # XOR brute-force often generates printable garbage; demand stronger text quality.
                alpha_ratio = _alpha_ratio(decoded)
                if alpha_ratio < 0.55:
                    s -= 20
                else:
                    s -= 10

                if use_ai_filter and AI_VALIDATION and s < 70:
                    continue

            s = max(0, min(100, s))
            
            current_path = f"{path} → {method}" if path else method
            
            results.append({
                "method": method,
                "decoded": decoded,
                "score": int(round(s)),  # Always return integer scores
                "layer": depth + 1,
                "chain": current_path,
                "ai_validated": use_ai_filter and AI_VALIDATION
            })

            # Improved multi-layer detection - recurse for encodings that could be layered
            should_recurse = False
            if depth < max_depth:  # Use the passed-in max_depth
                # Always recurse for common layered encodings
                if method in ["base64", "hex", "base32", "url", "morse"]:
                    # Check if decoded text matches encoding patterns or looks suspicious
                    if _looks_like_encoding(decoded) or depth < 2:
                        should_recurse = True

                # For classical ciphers, recurse only when output still looks encoded.
                if method in ["rot13", "caesar"] and _looks_like_encoding(decoded):
                    should_recurse = True
            
            if should_recurse and len(decoded) > 2 and len(decoded) < 15000:
                try:
                    nested_results = run_cipherx(decoded, depth + 1, current_path, use_ai_filter, max_depth)
                    results.extend(nested_results)
                except:
                    pass

    # Sort by score (AI confidence) - highest first
    results = _dedupe_results(results)
    
    # Return top 20 results to show more possibilities
    # All are now AI-validated to be real English!
    return results[:20]