import os

import psycopg
from pgvector.psycopg import register_vector

from repolens.chunking import Chunk


DATABASE_URL = os.getenv("DATABASE_URL","postgresql://repolens_user:postgres@localhost:5433/repolens_db")


def connect():
  conn = psycopg.connect(DATABASE_URL)
  register_vector(conn)
  return conn

def get_or_create_repo(conn : psycopg.Connection, owner:str, name:str, url:str) -> int:
  """Return the repo's id, creating the row if it doesn't exist yet."""
  row = conn.execute(
    """
    INSERT INTO repos (owner, name, url)
    VALUES (%s, %s, %s)
    ON CONFLICT (owner, name)
    DO UPDATE SET url = EXCLUDED.url
    RETURNING id
    """,
    (owner, name, url)
  ).fetchone()
  return row[0]

def get_or_create_branch(conn : psycopg.Connection, repo_id:int, branch_name:str) -> int:
  """Return the branch's id, creating the row (status 'queued') if it doesn't exist yet."""
  row = conn.execute(
    """
    INSERT INTO branches (repo_id,name)
    VALUES (%s,%s)
    ON CONFLICT (repo_id, name)
    DO UPDATE SET repo_id = EXCLUDED.repo_id
    RETURNING id
    """,
    (repo_id, branch_name)
  ).fetchone()
  return row[0]

def get_branch(conn:psycopg.Connection,branch_id:int)->tuple | None:
  row = conn.execute(
    """
    SELECT r.name, r.owner, b.status
    FROM branches b join repos r
    on b.repo_id = r.id
    where b.id = %s
    """,
    (branch_id,)
  ).fetchone()
  return row


def save_index(
  conn: psycopg.Connection,
  branch_id: int,
  files: dict[str, str],
  chunks: list[Chunk],
  embed_model: str,
  commit_sha: str | None = None,
) -> None:
  """Store a branch's files and embedded chunks, then mark it ready. All or nothing."""
  if any(c.embedding is None for c in chunks):
    raise ValueError("every chunk needs an embedding before saving")

  with conn.transaction():  # commits if the block finishes, rolls back if anything raises
    _replace_files(conn, branch_id, files)
    _replace_chunks(conn, branch_id, chunks)
    _mark_ready(conn, branch_id, len(chunks), embed_model, commit_sha)


def _replace_files(conn: psycopg.Connection, branch_id: int, files: dict[str, str]) -> None:
  # Re-indexing a branch: drop the old rows first, or the new ones pile on top.
  conn.execute("DELETE FROM files WHERE branch_id = %s", (branch_id,))
  with conn.cursor() as cur:
    cur.executemany(
      "INSERT INTO files (branch_id, path, content) VALUES (%s, %s, %s)",
      [(branch_id, path, content) for path, content in files.items()],
    )


def _replace_chunks(conn: psycopg.Connection, branch_id: int, chunks: list[Chunk]) -> None:
  conn.execute("DELETE FROM chunks WHERE branch_id = %s", (branch_id,))
  with conn.cursor() as cur:
    cur.executemany(
      """
      INSERT INTO chunks (branch_id, path, start_line, end_line, content, embedding)
      VALUES (%s, %s, %s, %s, %s, %s)
      """,
      # register_vector lets a plain list of floats go into the vector column
      [(branch_id, c.path, c.start_line, c.end_line, c.content, c.embedding) for c in chunks],
    )


def _mark_ready(
  conn: psycopg.Connection, branch_id: int, total_chunks: int, embed_model: str, commit_sha: str | None
) -> None:
  conn.execute(
    """
    UPDATE branches
    SET status = 'ready',
        error = NULL,
        total_chunks = %s,
        embed_model = %s,
        commit_sha = %s,
        indexed_at = now()
    WHERE id = %s
    """,
    (total_chunks, embed_model, commit_sha, branch_id),
  )


def search_chunks(
  conn: psycopg.Connection, branch_id: int, question_embedding: list[float], k: int
) -> list[tuple[float, Chunk]]:
  """Return the k chunks of one branch closest to the question, as (score, chunk), best first.

  Same shape as retrieval.search, so build_prompt and build_sources work unchanged.
  """
  rows = conn.execute(
    """
    SELECT path, start_line, end_line, content,
           1 - (embedding <=> %(q)s::vector) AS score    -- cosine similarity, 1 = same direction %(q)s::vector - it converts the oytho list to pgvector vector so that <=> can compare
    FROM chunks
    WHERE branch_id = %(branch_id)s
    ORDER BY embedding <=> %(q)s::vector                 -- distance, smallest first
    LIMIT %(k)s
    """,
    {"q": question_embedding, "branch_id": branch_id, "k": k},
  ).fetchall()
  return [
    (score, Chunk(start_line=start, end_line=end, content=content, path=path))
    for path, start, end, content, score in rows
  ]

def load_files(conn : psycopg.Connection, branch_id:str)->dict[str,str]:
  rows = conn.execute(
    """
      SELECT path, content from files WHERE branch_id = %s
    """,
    (branch_id,)
  ).fetchall()
  return dict(rows)



