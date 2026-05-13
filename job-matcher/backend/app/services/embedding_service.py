"""Embedding generation service using OpenAI."""

from typing import List, Optional
import numpy as np

from openai import AsyncOpenAI

from app.core.config import settings

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY) if settings.OPENAI_API_KEY else None


async def generate_embedding(text: str) -> Optional[List[float]]:
    """Generate an embedding vector for the given text."""
    if not client:
        return np.random.randn(settings.EMBEDDING_DIMENSIONS).tolist()

    text = text[:8000]

    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=text,
    )
    return response.data[0].embedding


async def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Generate embeddings for a batch of texts."""
    if not client:
        return [np.random.randn(settings.EMBEDDING_DIMENSIONS).tolist() for _ in texts]

    texts = [t[:8000] for t in texts]

    response = await client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts,
    )
    return [item.embedding for item in response.data]


def cosine_similarity(vec_a: List[float], vec_b: List[float]) -> float:
    """Compute cosine similarity between two vectors."""
    a = np.array(vec_a)
    b = np.array(vec_b)
    dot = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return float(dot / (norm_a * norm_b))
