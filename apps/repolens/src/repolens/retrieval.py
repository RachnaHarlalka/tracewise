from repolens.chunking import Chunk
from repolens.embeddings import cosine_similarity, embed_data


def search(question: str, chunks: list[Chunk], k: int = 5) -> list[tuple[float, Chunk]]:
  """Return the k chunks most similar to the question as (score, chunk), best first."""
  question_embedding = embed_data(question)[0]
  # Scores live here, not on the chunks, so a second search can't overwrite them.
  scored = [
    (cosine_similarity(question_embedding, chunk.embedding), chunk)
    for chunk in chunks
    if chunk.embedding is not None
  ]
  scored.sort(key=lambda pair: pair[0], reverse=True)
  return scored[:k]







