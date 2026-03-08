"""
AI Validator Module - Validates text quality to filter garbage results
"""

from scorer import score_text
import string
import re

def _looks_like_encoding(text):
    """Check if text looks like it could be another layer of encoding"""
    if not text or len(text) < 4:
        return False
    
    text_stripped = text.strip()
    
    # Check for Base64 pattern
    if re.fullmatch(r'[A-Za-z0-9+/=]+', text_stripped) and len(text_stripped) % 4 == 0:
        return True
    
    # Check for Hex pattern
    if re.fullmatch(r'[0-9a-fA-F]+', text_stripped) and len(text_stripped) % 2 == 0:
        return True
    
    # Check for Base32 pattern
    if re.fullmatch(r'[A-Z2-7=]+', text_stripped) and len(text_stripped) % 8 == 0:
        return True
    
    # Check for URL encoding
    if re.search(r'%[0-9A-Fa-f]{2}', text):
        return True
    
    return False

def validate_text_quality(text):
    """
    Validate if the decoded text is likely valid English/language text
    OR if it looks like another layer of encoding (for multi-layer decode)
    Returns: (is_valid, confidence, reason)
    """
    if not text or len(text) == 0:
        return False, 0, "Empty text"
    
    # IMPORTANT: If text looks like another encoding, allow it through for multi-layer decoding
    if _looks_like_encoding(text):
        # Give it a medium score so it can be recursively decoded
        return True, 50, "Possible multi-layer encoding"
    
    # Get score from scorer
    score = score_text(text)
    
    # Calculate printable ratio
    printable_count = sum(1 for c in text if c in string.printable)
    printable_ratio = printable_count / len(text) if len(text) > 0 else 0
    
    # Check if mostly printable
    if printable_ratio < 0.7:
        return False, score, "Too many non-printable characters"
    
    # Adaptive threshold: lower for short texts (abbreviations, codes, signals like "SOS")
    # Short texts (< 20 chars) often have low scores but can be valid decoded content
    text_stripped = text.strip()
    if len(text_stripped) < 20:
        # For short texts, accept if score >= 30 and mostly alphanumeric/space
        alphanumeric_space_count = sum(1 for c in text_stripped if c.isalnum() or c.isspace())
        alphanumeric_ratio = alphanumeric_space_count / len(text_stripped) if len(text_stripped) > 0 else 0
        
        if alphanumeric_ratio >= 0.8:
            is_valid = score >= 30
        else:
            is_valid = score >= 60
    else:
        # For longer texts, use standard threshold
        is_valid = score >= 60
    
    reason = "Valid text" if is_valid else "Low quality score"
    
    return is_valid, score, reason

def filter_results(results, min_confidence=60):
    """
    Filter results to only keep high-quality decodings
    """
    filtered = []
    for result in results:
        decoded = result.get('decoded', '')
        is_valid, confidence, reason = validate_text_quality(decoded)
        
        if is_valid and confidence >= min_confidence:
            result['ai_confidence'] = confidence
            result['ai_reason'] = reason
            filtered.append(result)
    
    return filtered
