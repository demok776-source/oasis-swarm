import hashlib
import random
import os
import json
import urllib.request
import urllib.error
from src.utils.logger import get_logger

logger = get_logger("embeddings")

def get_embedding(text: str) -> list[float]:
    """
    Generate a 1536-dimensional embedding for the given text.
    If OPENAI_API_KEY is available in the environment, it uses OpenAI's API.
    Otherwise, it generates a deterministic mock vector of the same dimension.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            logger.info("Generating embedding via OpenAI API...")
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "input": text,
                "model": "text-embedding-3-small"
            }
            
            req = urllib.request.Request(
                "https://api.openai.com/v1/embeddings",
                data=json.dumps(payload).encode("utf-8"),
                headers=headers,
                method="POST"
            )
            
            with urllib.request.urlopen(req, timeout=10.0) as response:
                resp_data = json.loads(response.read().decode("utf-8"))
                logger.info("OpenAI embedding generated successfully.")
                return resp_data["data"][0]["embedding"]
                
        except urllib.error.URLError as ue:
            logger.error(f"OpenAI API network/URL error: {ue}. Falling back to mock generator.")
        except Exception as e:
            logger.error(f"Failed to generate OpenAI embedding: {e}. Falling back to mock generator.")

    # Deterministic mock fallback (1536 dimensions)
    logger.debug("Generating mock deterministic embedding...")
    hasher = hashlib.sha256(text.encode("utf-8"))
    seed = int(hasher.hexdigest(), 16) % (2**32)
    rng = random.Random(seed)
    
    vec = [rng.uniform(-1.0, 1.0) for _ in range(1536)]
    norm = sum(x*x for x in vec) ** 0.5
    if norm > 0:
        vec = [x / norm for x in vec]
        
    return vec
