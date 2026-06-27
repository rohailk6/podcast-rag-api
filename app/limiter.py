from slowapi import Limiter
from fastapi import Request

def get_api_key_from_request(request: Request) -> str:
    """
    Tells slowapi HOW to identify each user.
    
    We extract the API key from the Authorization header.
    This is the same key your security.py already validates —
    so limits are per-user, not per-IP address.
    
    Why not use IP address?
    If 10 people share an office network, they'd share one counter.
    Using the API key means each user gets their own independent limit.
    
    The fallback to the IP is just a safety net — it should never
    actually be reached because security.py rejects keyless requests first.
    """
    auth_header = request.headers.get("Authorization", "")

    if auth_header.startswith("Bearer "):
        # Extract just the key part, strip Bearer prefix
        return auth_header[len("Bearer"):]
    
    # Fallback: use IP address (shouldn't reach here after auth)
    return request.client.host

# Create the limiter instance — imported by main.py and query.py
limiter = Limiter(key_func=get_api_key_from_request)