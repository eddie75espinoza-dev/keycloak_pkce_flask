import base64
import hashlib
import os


def generate_pkce_pair():
    code_verifier = base64.urlsafe_b64encode(os.urandom(32)).rstrip(b'=').decode('utf-8')
    sha256_hash = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(sha256_hash).rstrip(b'=').decode('utf-8')
    
    return code_verifier, code_challenge
