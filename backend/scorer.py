import string
import re

COMMON_WORDS = ["the", "flag", "ctf", "admin", "password", "user", "key", "secret", 
                "token", "and", "for", "that", "this", "with", "from", "have", "are",
                "you", "not", "but", "can", "was", "all", "were", "when", "we", "there",
                "been", "will", "what", "which", "their", "said", "each", "she", "how",
                "because", "did", "these", "would", "could", "should", "about", "security",
                "system", "data", "encryption", "cyber", "network", "attack", "threat"]

COMMON_BIGRAMS = ["th", "he", "in", "er", "an", "re", "on", "at", "en", "nd", "ti", "es", "or", "te", "of",
                  "ed", "is", "it", "al", "ar", "st", "to", "nt", "ng", "se", "ha", "as", "ou", "io", "le"]

COMMON_TRIGRAMS = ["the", "and", "ing", "ion", "tio", "ent", "ati", "for", "her", "ter",
                   "hat", "tha", "ere", "ate", "his", "con", "res", "ver", "all", "ons"]

def printable_ratio(text):
    """Calculate ratio of printable characters"""
    if not text:
        return 0
    printable_count = sum(1 for c in text if c in string.printable and c not in '\x00\x01\x02\x03\x04\x05\x06\x07')
    return min(printable_count / max(len(text), 1), 1.0)

def english_score(text):
    """Score based on common English words"""
    if not text or len(text) < 2:
        return 0
    score = 0
    text_lower = text.lower()
    for word in COMMON_WORDS:
        if word in text_lower:
            score += 5
    return min(score, 30)

def bigram_score(text):
    """Score based on common English bigrams"""
    if not text or len(text) < 2:
        return 0
    score = 0
    text_lower = text.lower()
    for bigram in COMMON_BIGRAMS:
        score += text_lower.count(bigram) * 1
    return min(score, 25)

def trigram_score(text):
    """Score based on common English trigrams (critical for Caesar detection)"""
    if not text or len(text) < 3:
        return 0
    score = 0
    text_lower = text.lower()
    for trigram in COMMON_TRIGRAMS:
        score += text_lower.count(trigram) * 2
    return min(score, 25)

def flag_bonus(text):
    """Bonus for flag patterns"""
    patterns = [
        r'(?i)flag\{[^}]+\}',
        r'(?i)ctf\{[^}]+\}',
        r'[A-Z0-9]{32}',  # MD5-like hash
        r'(?i)picoctf\{[^}]+\}',
        r'[A-Za-z]{3,10}\{[A-Za-z0-9_\-]+\}'
    ]
    for p in patterns:
        if re.search(p, text):
            return 50  # High score for flags
    return 0

def word_ratio(text):
    """Ratio of dictionary-like words"""
    if not text:
        return 0
    words = re.findall(r'\b[a-zA-Z]{3,}\b', text)
    if not words:
        return 0
    return min(len(words) * 2, 15)

def get_english_words():
    """Load English dictionary for validation (cached)"""
    if not hasattr(get_english_words, '_cache'):
        try:
            import nltk
            nltk.data.find('corpora/words')
            from nltk.corpus import words
            get_english_words._cache = set(w.lower() for w in words.words())
        except:
            # Expanded fallback dictionary for better Caesar detection
            get_english_words._cache = set(COMMON_WORDS + [
                'is', 'it', 'to', 'of', 'in', 'on', 'at', 'be', 'by', 'or', 'up', 'as',
                'do', 'go', 'if', 'me', 'my', 'no', 'so', 'we', 'he', 'hi', 'an', 'all',
                'get', 'has', 'had', 'can', 'out', 'now', 'who', 'why', 'how', 'which',
                'their', 'them', 'then', 'than', 'more', 'most', 'some', 'such', 'could',
                'would', 'should', 'about', 'after', 'before', 'during', 'between',
                'into', 'through', 'over', 'also', 'back', 'only', 'come', 'made', 'find',
                'use', 'may', 'water', 'long', 'little', 'very', 'after', 'word', 'just',
                'where', 'most', 'know', 'get', 'through', 'back', 'much', 'good', 'new',
                'write', 'our', 'used', 'many', 'them', 'these', 'make', 'like', 'him',
                'see', 'time', 'has', 'look', 'two', 'more', 'go', 'come', 'number', 'way',
                'people', 'said', 'each', 'she', 'well', 'because', 'turn', 'here', 'why',
                'ask', 'went', 'men', 'read', 'need', 'land', 'different', 'home', 'move',
                'try', 'kind', 'hand', 'picture', 'again', 'change', 'off', 'play', 'spell',
                'air', 'away', 'animal', 'house', 'point', 'page', 'letter', 'mother', 'answer'
            ])
    return get_english_words._cache

def english_word_match_ratio(text):
    """Score by matching actual English words (critical for Caesar)"""
    if not text or len(text) < 3:
        return 0
    
    words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
    if not words:
        return 0
    
    english_words = get_english_words()
    matched = sum(1 for w in words if w in english_words)
    
    # Return percentage of matched words with higher weight for Caesar
    ratio = matched / len(words) if words else 0
    
    # Bonus for high match percentage
    score = ratio * 50  # Increased from 40
    if ratio > 0.7:  # More than 70% words are English
        score += 15  # Big bonus for strong English text
    
    return min(score, 50)  # Increased cap from 30 to 50

def score_text(text):
    """
    SUPER OPTIMIZED AI scoring function.
    Enhanced with trigrams and improved weights for perfect Caesar detection.
    """
    if not text or len(text) == 0:
        return 0
    
    # Check for flag first
    flag_score = flag_bonus(text)
    if flag_score > 0:
        return min(flag_score + printable_ratio(text) * 5, 100)
    
    # Enhanced multi-factor scoring
    printable = printable_ratio(text) * 20  # Reduced to make room for other factors
    english_dict = english_word_match_ratio(text)  # 0-50 points (highest weight)
    english = english_score(text)  # 0-30 points
    bigrams = bigram_score(text)  # 0-25 points
    trigrams = trigram_score(text)  # 0-25 points (NEW - critical for Caesar)
    words = word_ratio(text)  # 0-15 points
    
    # Calculate total with all factors
    total = printable + english_dict + english + bigrams + trigrams + words
    
    # Bonus for very high English content (Caesar/ROT13 perfect detection)
    if english_dict > 40 and trigrams > 15:
        total = min(total + 10, 100)  # Perfect English bonus
    
    return min(total, 100)
