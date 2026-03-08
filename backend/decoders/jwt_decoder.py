import base64
import json

def decode_jwt(text):
    """JWT token decoder - extracts header and payload"""
    try:
        parts = text.split('.')
        if len(parts) != 3:
            return []
        
        results = []
        
        # Decode header
        header_padding = parts[0] + '=' * (4 - len(parts[0]) % 4)
        header = base64.urlsafe_b64decode(header_padding).decode('utf-8')
        
        # Decode payload
        payload_padding = parts[1] + '=' * (4 - len(parts[1]) % 4)
        payload = base64.urlsafe_b64decode(payload_padding).decode('utf-8')
        
        combined = f"Header: {header}\nPayload: {payload}"
        results.append(combined)
        
        # Also return just the payload as it often contains the flag
        results.append(payload)
        
        return results
    except:
        return []
