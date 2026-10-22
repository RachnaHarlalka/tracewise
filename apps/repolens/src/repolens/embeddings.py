import math
from repolens.config import EMBEDDING_MODEL_NAME
from repolens.llm import call_embedding_model



def embed_data(data):
  response = call_embedding_model(model_name=EMBEDDING_MODEL_NAME,texts=data)
  vectors = response.embeddings
  return vectors


def cosine_similarity(v1:list[float],v2:list[float]):
  dot = sum(x*y for x, y in zip(v1,v2))
  len_v1 = math.sqrt(sum(x*x for x in v1))
  len_v2 = math.sqrt(sum(y*y for y in v2))
  return dot/ (len_v1 * len_v2)



