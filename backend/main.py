from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import re
import base64
import os
from typing import List, Dict, Optional
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Import NEW AI-powered engine
try:
    from engine import run_cipherx
    AI_ENGINE = True
except ImportError:
    AI_ENGINE = False

# Import CipherX professional operations engine
try:
    from cipherx_ops_extended import OPERATIONS, execute_operation
    EXTENDED_OPS = True
except ImportError:
    from cipherx_ops_core import OPERATIONS, execute_operation
    EXTENDED_OPS = False

# Import improved AI scorer
try:
    from scorer import score_text
    AI_SCORER = True
except ImportError:
    AI_SCORER = False

app = FastAPI()

# Frontend path (served by backend for single-link local run)
BACKEND_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_DIR = os.path.dirname(BACKEND_DIR)
FRONTEND_DIR = os.path.join(PROJECT_DIR, "frontend")
FRONTEND_INDEX = os.path.join(FRONTEND_DIR, "index.html")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8080",
        "http://localhost:8080",
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://127.0.0.1:8080",
        "https://localhost:8080",
    ],
    allow_origin_regex=r"https://.*\.ngrok-free\.app|https://.*\.ngrok\.io",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve frontend assets from backend so app works on a single URL.
if os.path.isdir(FRONTEND_DIR):
    from fastapi.staticfiles import StaticFiles
    # Custom StaticFiles to disable caching for development
    app.mount("/assets", StaticFiles(directory=FRONTEND_DIR, html=True), name="assets")


class TextInput(BaseModel):
    text: str
    deep: bool = False

class EncodeInput(BaseModel):
    text: str
    operation: str
    params: Optional[Dict] = {}

class RecipeInput(BaseModel):
    text: str
    operations: List[Dict]  # List of {operation: str, params: dict}

def detect_encoding(text: str) -> List[str]:
    """
    AI-powered encoding detection with extended support
    Returns list of likely encodings ordered by confidence
    """
    detected = []
    text_stripped = text.strip()
    
    # Gzip detection (if looks like base64 and starts with 'H4sI')
    if text_stripped.startswith('H4sI'):
        detected.append('from_gzip')
    
    # Zlib detection (base64 that starts with 'eJ')
    if text_stripped.startswith('eJ'):
        detected.append('from_zlib')
    
    # Base85 detection (contains special chars used in base85)
    if re.match(r'^[!-u]+$', text_stripped):
        detected.append('from_base85')
    
    # Base64 detection
    # Base64 detection - allow URL-safe characters and some noise
    if re.search(r'[A-Za-z0-9+/=_-]{4,}', text_stripped):
        # Clean string to check length logic
        clean_b64 = re.sub(r'[^A-Za-z0-9+/=_]', '', text_stripped)
        if len(clean_b64) >= 4: # Minimum length for meaningful base64
            detected.append('from_base64')
            # Check for double encoding
            detected.append('double_base64_decode')
            detected.append('hex_base64_decode')
    
    # Base32 detection (only A-Z and 2-7)
    if re.match(r'^[A-Z2-7]+=*$', text_stripped) and len(text_stripped) % 8 == 0:
        detected.append('from_base32')
    
    # Base58 detection (Bitcoin-style, no 0OIl)
    if re.match(r'^[1-9A-HJ-NP-Za-km-z]+$', text_stripped):
        detected.append('from_base58')
    
    # Hex detection
    if re.match(r'^[0-9a-fA-F\s:-]+$', text_stripped) and len(text_stripped.replace(' ', '').replace(':', '').replace('-', '')) % 2 == 0:
        detected.append('from_hex')
    
    # Binary detection
    if re.match(r'^[01\s]+$', text_stripped) and len(text_stripped.replace(' ', '').replace('\n', '')) % 8 == 0:
        detected.append('from_binary')
    
    # URL encoded detection
    if '%' in text and re.search(r'%[0-9a-fA-F]{2}', text):
        detected.append('from_url')
    
    # HTML entities detection
    if '&' in text and ';' in text and re.search(r'&[#a-zA-Z0-9]+;', text):
        detected.append('from_html')
    
    # Morse code detection
    if re.match(r'^[.\-/\s]+$', text_stripped):
        detected.append('from_morse')
    
    # ASCII codes detection (space-separated numbers)
    if re.match(r'^[\d\s]+$', text_stripped):
        detected.append('from_ascii_codes')
    
    # UTF-8 hex bytes detection
    if re.match(r'^[0-9a-fA-F\s]+$', text_stripped):
        detected.append('from_utf8_bytes')
    
    # JWT detection (header.payload.signature format)
    if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', text_stripped):
        detected.insert(0, 'from_jwt')  # High priority
    
    # Unicode escape sequences detection (\uXXXX format)
    if re.search(r'\\u[0-9a-fA-F]{4}', text_stripped):
        detected.insert(0, 'from_unicode')  # High priority
    
    # Classical ciphers (if text has letters)
    if any(c.isalpha() for c in text):
        detected.extend(['rot13', 'atbash', 'caesar_bruteforce'])
    
    # Reversed text detection
    reversed_text = text[::-1]
    if any(word in reversed_text.lower() for word in ['flag', 'the', 'http', 'www', 'ctf']):
        detected.insert(0, 'reverse')  # High priority
    
    return detected

def score_output(text: str) -> float:
    """
    Score the output using improved AI scorer with English dictionary matching
    """
    try:
        # Always try to use improved scorer  
        return score_text(text)
    except:
        # If anything fails, return 0 instead of fallback scoring
        return 0

@app.get("/")
async def root():
    """Serve frontend app when available; fallback to API info endpoint."""
    if os.path.isfile(FRONTEND_INDEX):
        return FileResponse(FRONTEND_INDEX)
    return await api_info()

@app.get("/api")
async def api_info():
    """List all available operations"""
    ops_info = {}
    
    # Categorize operations
    categories = {
        "Encoding": [],
        "Classical Ciphers": [],
        "Modern Encryption": [],
        "Hashing": [],
        "Compression": [],
        "Obfuscation": [],
        "String Operations": [],
        "Extraction": []
    }
    
    for name in OPERATIONS.keys():
        if name.startswith('from_') or name.startswith('to_'):
            if 'base' in name or 'hex' in name or 'binary' in name or 'url' in name or 'html' in name or 'ascii' in name or 'utf8' in name:
                categories["Encoding"].append(name)
            elif 'gzip' in name or 'zlib' in name:
                categories["Compression"].append(name)
        elif 'rot' in name or 'caesar' in name or 'atbash' in name or 'vigenere' in name or 'rail' in name or 'affine' in name or 'morse' in name:
            categories["Classical Ciphers"].append(name)
        elif 'aes' in name or 'des' in name or 'rsa' in name:
            categories["Modern Encryption"].append(name)
        elif 'md5' in name or 'sha' in name or 'blake' in name or 'bcrypt' in name:
            categories["Hashing"].append(name)
        elif 'xor' in name or 'double' in name:
            categories["Obfuscation"].append(name)
        elif 'extract' in name or 'remove' in name or 'upper' in name or 'lower' in name:
            categories["String Operations"].append(name)
    
    return {
        "app": "CipherX - Extended CyberChef Alternative",
        "version": "3.0",
        "status": "online",
        "total_operations": len(OPERATIONS),
        "extended_mode": EXTENDED_OPS,
        "categories": categories,
        "all_operations": list(OPERATIONS.keys())
    }


# Extraction operations to try during auto-decode when input is plain text
_EXTRACTION_OPS = {
    'extract_emails': ('Emails', '📧'),
    'extract_urls': ('URLs', '🔗'),
    'extract_ips': ('IP Addresses', '🌐'),
    'extract_md5s': ('MD5 Hashes', '#️⃣'),
    'extract_sha256s': ('SHA256 Hashes', '#️⃣'),
    'extract_base64s': ('Base64 Strings', '🔤'),
}

def _try_extractions(text):
    """Run extraction operations on plain text and return formatted results."""
    results = []
    for op_name, (label, emoji) in _EXTRACTION_OPS.items():
        if op_name not in OPERATIONS:
            continue
        try:
            extracted = execute_operation(op_name, text)
            if extracted and extracted.strip():
                items = [item for item in extracted.strip().split('\n') if item.strip()]
                if op_name == 'extract_base64s':
                    items = [item for item in items if _is_confident_base64_candidate(item)]
                unique_items = list(dict.fromkeys(items))
                if unique_items:
                    display = f"{emoji} Extracted {label}: {len(unique_items)} unique item(s)\n"
                    display += "-" * 40 + "\n"
                    display += "\n".join(unique_items)
                    results.append({
                        "method": f"Extract {label}",
                        "operation": op_name,
                        "decoded": display,
                        "score": 95,
                        "confidence": 95,
                        "layer": 1,
                        "chain": f"Extract {label}",
                        "length": len(display),
                        "ai_validated": True
                    })
        except Exception:
            continue
    return results


def _is_strict_base64_like(text):
    if not text:
        return False
    t = text.strip()
    if not re.fullmatch(r'[A-Za-z0-9+/=_-]+', t):
        return False
    return len(t) >= 8 and len(t) % 4 == 0


def _is_strict_hex_like(text):
    if not text:
        return False
    t = re.sub(r"\s+", "", text.strip())
    return len(t) >= 8 and len(t) % 2 == 0 and re.fullmatch(r"[0-9a-fA-F]+", t) is not None


def _looks_like_encoded_payload(text):
    if not text:
        return False
    t = text.strip()
    if _is_strict_base64_like(t) or _is_strict_hex_like(t):
        return True
    if re.fullmatch(r"[A-Z2-7=]+", t.upper()) and len(t) >= 8:
        return True
    if re.search(r"%[0-9A-Fa-f]{2}", t):
        return True
    return False


def _is_confident_base64_candidate(text):
    """Avoid treating plain alphabetic words as Base64 extraction hits."""
    if not _is_strict_base64_like(text):
        return False
    t = text.strip()

    # Very short matches from plaintext (e.g., URL fragments like "8000/api")
    # are usually false positives.
    if len(s) < 12:
        return False
    return '=' in t or bool(re.search(r'[0-9+/_-]', t))


def _looks_like_classical_cipher_input(text):
    """Heuristic for Caesar/ROT/Atbash style payloads (incl. CTF flag punctuation)."""
    if not text:
        return False
    t = text.strip()
    if len(t) < 6:
        return False

    # Allow common punctuation found in flags/sentences.
    if not re.fullmatch(r"[A-Za-z0-9\s_{}\-.,:;!?']+", t):
        return False

    alpha = sum(1 for c in t if c.isalpha())
    ratio = alpha / max(len(t), 1)
    return ratio >= 0.5


def _prioritize_results_for_encoded_input(text, results):
    """Re-rank results to prefer deterministic decoders for obvious encoded payloads."""
    if not results:
        return results

    deterministic = {"base64", "base32", "hex", "binary", "url", "jwt", "unicode", "morse"}
    boosted = []

    strict_b64 = _is_strict_base64_like(text)
    strict_hex = _is_strict_hex_like(text)
    classical_like = _looks_like_classical_cipher_input(text)
    
    # Don't boost classical ciphers if input is ALREADY readable English
    input_score = score_text(text)
    boost_classical = classical_like and input_score < 70
    
    for r in results:
        rr = dict(r)
        method = rr.get("method", "")
        score = rr.get("score", 0)

        if method in deterministic:
            score += 25
        if strict_b64 and method == "base64":
            score += 40
        if strict_b64 and method == "xor":
            score -= 40
        if strict_b64 and method == "reverse":
            score -= 50

        # For strict hex input, if direct hex decode still looks encoded,
        # prefer downstream decoded plaintext results.
        if strict_hex and method == "hex":
            decoded_text = rr.get("decoded", "")
            if _looks_like_encoded_payload(decoded_text):
                score -= 35

        if boost_classical and method in {"caesar", "rot13", "atbash"}:
            score += 30
        if boost_classical and method == "xor":
            score -= 35
        # Only demote reverse if it has a weak score (likely garbage).
        # If reverse already produced high-confidence plaintext (score >= 75),
        # don't demote it — it's probably the correct answer.
        if boost_classical and method == "reverse" and score < 75:
            score -= 25

        rr["score"] = max(0, min(100, int(round(score))))
        boosted.append(rr)

    boosted.sort(key=lambda x: x.get("score", 0), reverse=True)
    return boosted


@app.post("/decode")
async def decode(input_data: TextInput):
    """
    Auto-detect and decode text using AI-POWERED ENGINE
    Returns only VALID English results (filters garbage automatically!)
    """
    text = input_data.text.strip()
    
    if not text:
        raise HTTPException(status_code=400, detail="Input text is empty")
    
    # Use NEW AI-powered engine if available
    if AI_ENGINE:
        try:
            # Pass deep analysis flag to engine (5 layers if deep, 2 if normal)
            results = run_cipherx(text, use_ai_filter=True, max_depth=5 if input_data.deep else 2) 
            
            # If AI filtered EVERYTHING, check if input is already readable text.
            # If so, don't fall back to unfiltered mode (which returns XOR garbage).
            if not results:
                input_score = score_output(text) if not AI_SCORER else score_text(text)
                if input_score < 35:
                    # Input is likely encoded — fall back to unfiltered mode
                    results = run_cipherx(text, use_ai_filter=False, max_depth=5 if input_data.deep else 2)

            # Re-rank for obviously encoded inputs (e.g., strict base64)
            results = _prioritize_results_for_encoded_input(text, results)
            
            # Always try extractions (emails, URLs, IPs, etc.)
            extraction_results = _try_extractions(text)
            
            if not results:
                # No decode results at all — return extractions if any
                if extraction_results:
                    return {
                        "success": True,
                        "message": f"Found {len(extraction_results)} extraction result(s)",
                        "results": extraction_results
                    }
                return {
                    "success": False,
                    "message": "No valid text found.",
                    "results": []
                }
            
            # If input is readable plaintext, prefer extractions only over clearly
            # weak decode results. Strong classical decodes like ROT13/Caesar/Atbash
            # should still win when they produce high-confidence plaintext.
            if extraction_results:
                input_score = score_text(text) if AI_SCORER else score_output(text)
                # Check if best decode is just a weak transform
                best_method = results[0].get('method', '') if results else ''
                best_score = results[0].get('score', 0) if results else 0
                best_decoded = results[0].get('decoded', '') if results else ''
                best_is_noop = best_decoded.strip() == text.strip()
                weak_methods = {'reverse', 'xor'}
                if input_score >= 35 and (best_method in weak_methods or best_score < 80 or best_is_noop):
                    # Input is plaintext — extractions are more useful
                    return {
                        "success": True,
                        "message": f"Found {len(extraction_results)} extraction result(s)",
                        "results": extraction_results
                    }
            
            # Format results for frontend
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "method": r.get('method', 'unknown').replace('_', ' ').title(),
                    "operation": r.get('method', 'unknown'),
                    "decoded": r.get('decoded', '')[:1000],
                    "score": r.get('score', 0),
                    "confidence": r.get('score', 0),
                    "layer": r.get('layer', 1),
                    "chain": r.get('chain', ''),
                    "length": len(r.get('decoded', '')),
                    "ai_validated": r.get('ai_validated', True)
                })
            
            return {
                "success": True,
                "message": f"Found {len(formatted_results)} valid result(s) (AI-validated)",
                "results": formatted_results
            }
        except Exception as e:
            # Fallback to old method if error
            print(f"AI engine error: {e}")
            pass
    
    # FALLBACK: Old method (if AI engine not available)
    text_stripped = text
    results = []
    
    # Detect likely encodings
    detected_encodings = detect_encoding(text)
    
    # Also try JWT decoding if it looks like a JWT token
    if re.match(r'^[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+$', text_stripped):
        detected_encodings.insert(0, 'from_jwt')
    
    # Try each detected encoding
    for operation in detected_encodings[:15]:  # Limit to top 15 to avoid slowdown
        if operation not in OPERATIONS:
            continue
            
        try:
            decoded = execute_operation(operation, text)
            if decoded and decoded != text and not decoded.startswith("Error"):
                
                # SPECIAL HANDLING: Split Caesar bruteforce into individual shifts
                if operation == 'caesar_bruteforce':
                    # Parse individual shifts and score each separately
                    shifts = re.findall(r'Shift (\d+): (.+?)(?=\nShift \d+:|$)', decoded, re.DOTALL)
                    if shifts:
                        for shift_num, shift_text in shifts:
                            shift_text = shift_text.strip()
                            confidence = score_output(shift_text)
                            if confidence > 15:
                                results.append({
                                    "method": f"Caesar Shift {shift_num}",
                                    "operation": "caesar",
                                    "decoded": f"Shift {shift_num}: {shift_text}",
                                    "score": round(confidence, 2),
                                    "confidence": round(confidence, 2),
                                    "layer": 1,
                                    "chain": f"Caesar Shift {shift_num}",
                                    "length": len(shift_text)
                                })
                    continue
                
                # NORMAL HANDLING: Other operations
                confidence = score_output(decoded)
                if confidence > 15:  # Only include if decent confidence
                    results.append({
                        "method": operation.replace('from_', '').replace('_', ' ').title(),
                        "operation": operation,
                        "decoded": decoded[:1000],  # Limit output size
                        "score": round(confidence, 2),  # For frontend compatibility
                        "confidence": round(confidence, 2),  # Also include new field
                        "layer": 1,  # Auto-decode is layer 1
                        "chain": operation.replace('from_', '').replace('_', ' ').title(),
                        "length": len(decoded)
                    })
        except Exception as e:
            continue
    
    # Sort by confidence
    results.sort(key=lambda x: x['confidence'], reverse=True)
    
    if not results:
        # Try extraction operations before giving up
        extraction_results = _try_extractions(text)
        if extraction_results:
            return {
                "success": True,
                "message": f"Found {len(extraction_results)} extraction result(s)",
                "results": extraction_results
            }
        return {
            "success": False,
            "message": "Could not decode text with any known method",
            "tried_methods": detected_encodings[:10],
            "results": []
        }
    
    return {
        "success": True,
        "input_length": len(text),
        "detected_methods": len(results),
        "results": results[:10]  # Return top 10 results
    }

@app.post("/encode")
async def encode(input_data: EncodeInput):
    """
    Encode text using specified operation
    """
    text = input_data.text
    operation = input_data.operation
    params = input_data.params or {}
    
    if operation not in OPERATIONS:
        raise HTTPException(
            status_code=400, 
            detail=f"Unknown operation: {operation}. Use GET / to see all operations"
        )
    
    try:
        result = execute_operation(operation, text, **params)
        if result is None or (isinstance(result, str) and result.startswith("Error")):
            # For extraction operations, None/empty means no matches — not an error
            if operation.startswith('extract_'):
                return {
                    "success": True,
                    "operation": operation,
                    "input": text[:200] + "..." if len(text) > 200 else text,
                    "output": "",
                    "length": 0
                }
            raise HTTPException(status_code=400, detail=f"Operation failed: {result}")
        
        return {
            "success": True,
            "operation": operation,
            "input": text[:200] + "..." if len(text) > 200 else text,
            "output": result[:1000] + "..." if len(str(result)) > 1000 else result,
            "length": len(str(result))
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipe")
async def execute_recipe(input_data: RecipeInput):
    """
    Execute a chain of operations (CyberChef recipe)
    
    Example:
    {
        "text": "Hello World",
        "operations": [
            {"operation": "to_base64", "params": {}},
            {"operation": "to_hex", "params": {}},
            {"operation": "reverse", "params": {}}
        ]
    }
    """
    text = input_data.text
    operations = input_data.operations
    
    if not operations:
        raise HTTPException(status_code=400, detail="No operations specified")
    
    steps = []
    current = text
    
    for i, op_config in enumerate(operations):
        operation = op_config.get("operation")
        params = op_config.get("params", {})
        
        if operation not in OPERATIONS:
            return {
                "success": False,
                "error": f"Unknown operation at step {i+1}: {operation}",
                "completed_steps": steps
            }
        
        try:
            result = execute_operation(operation, current, **params)
            if result is None:
                return {
                    "success": False,
                    "error": f"Operation failed at step {i+1}: {operation}",
                    "completed_steps": steps
                }
            
            steps.append({
                "step": i + 1,
                "operation": operation,
                "input_preview": current[:100] + "..." if len(current) > 100 else current,
                "output_preview": str(result)[:100] + "..." if len(str(result)) > 100 else str(result),
                "output_length": len(str(result))
            })
            
            current = result
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Error at step {i+1}: {str(e)}",
                "completed_steps": steps
            }
    
    return {
        "success": True,
        "total_steps": len(steps),
        "steps": steps,
        "final_output": current
    }

@app.get("/operations")
async def list_operations():
    """List all available operations with categories"""
    categories = {
        "Encoding (Basic)": [k for k in OPERATIONS.keys() if any(x in k for x in ['base64', 'base32', 'base58', 'base85', 'hex', 'binary'])],
        "Encoding (Text)": [k for k in OPERATIONS.keys() if any(x in k for x in ['url', 'html', 'ascii', 'utf8'])],
        "Classical Ciphers": [k for k in OPERATIONS.keys() if any(x in k for x in ['rot', 'caesar', 'atbash', 'vigenere', 'rail', 'affine', 'morse'])],
        "Modern Encryption": [k for k in OPERATIONS.keys() if any(x in k for x in ['aes', 'des', 'rsa'])],
        "Hashing": [k for k in OPERATIONS.keys() if any(x in k for x in ['md5', 'sha', 'blake'])],
        "Compression": [k for k in OPERATIONS.keys() if any(x in k for x in ['gzip', 'zlib'])],
        "Obfuscation": [k for k in OPERATIONS.keys() if any(x in k for x in ['xor', 'double'])],
        "String Operations": [k for k in OPERATIONS.keys() if any(x in k for x in ['upper', 'lower', 'reverse', 'remove', 'extract'])],
        "JSON": [k for k in OPERATIONS.keys() if 'json' in k]
    }
    
    return {
        "total": len(OPERATIONS),
        "categories": categories,
        "all_operations": sorted(list(OPERATIONS.keys()))
    }

@app.get("/hash/{algorithm}")
async def hash_text(algorithm: str, text: str):
    """
    Quick hash endpoint
    Usage: GET /hash/md5?text=Hello
    """
    hash_ops = {
        'md5': 'md5',
        'sha1': 'sha1',
        'sha256': 'sha256',
        'sha512': 'sha512',
        'sha3-256': 'sha3_256',
        'sha3-512': 'sha3_512',
        'blake2b': 'blake2b',
        'blake2s': 'blake2s'
    }
    
    if algorithm not in hash_ops:
        raise HTTPException(status_code=400, detail=f"Unknown hash algorithm: {algorithm}")
    
    op = hash_ops[algorithm]
    result = execute_operation(op, text)
    
    return {
        "algorithm": algorithm,
        "input": text,
        "hash": result
    }

if __name__ == "__main__":
    import uvicorn
    import sys
    import webbrowser
    import threading
    import time

    # Check if there are command line arguments (CLI mode)
    if len(sys.argv) > 1:
        input_text = " ".join(sys.argv[1:])
        print("\n" + "="*60)
        print("[*] CipherX CLI - AI Decoder")
        print("="*60)
        print(f"Input: {input_text}\n")
        
        try:
            from engine import run_cipherx
            results = run_cipherx(input_text, use_ai_filter=True)
            
            if not results:
                print("[X] No valid English results found.")
            else:
                print(f"Found {len(results)} potential result(s):\n")
                for i, r in enumerate(results[:5]):
                    print(f"[{i+1}] Method: {r['method'].upper()}")
                    print(f"    Confidence: {r['score']}%")
                    print(f"    Decoded: {r['decoded']}")
                    print("-" * 40)
        except ImportError:
            print("Error: Could not import decoding engine.")
        except Exception as e:
            print(f"Error during decoding: {e}")
        
        print("\nTo start the web interface, run 'python main.py' without arguments.")
        print("="*60 + "\n")
        sys.exit(0)

    # Server mode (No arguments)
    print("\n" + "="*60)
    print("[*] Starting CipherX AI Backend Server...")
    print("="*60)
    print("App URL: http://127.0.0.1:8000")
    
    def open_browser():
        time.sleep(1.5)  # Wait for server to initialize
        print("[*] Opening browser...")
        webbrowser.open("http://127.0.0.1:8000")

    # Start browser in a separate thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run Uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")

