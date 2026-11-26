-- RepoLens storage: one repo has many branches; each indexed branch has its files and chunks.
-- Runs once, when the Postgres volume is created (docker-entrypoint-initdb.d).
-- After changing it: docker compose down -v && docker compose up -d

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE repos (
  id SERIAL PRIMARY KEY,
  url TEXT NOT NULL,                      -- as given by the user, for display only
  owner TEXT NOT NULL,
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (owner, name)                    -- identifies the repo, whatever the URL spelling
);

CREATE TABLE branches (
  id SERIAL PRIMARY KEY,
  repo_id INTEGER NOT NULL REFERENCES repos(id) ON DELETE CASCADE,
  name TEXT NOT NULL,
  commit_sha TEXT,                        -- commit that was indexed; compare with GitHub to detect stale
  embed_model TEXT,                       -- model that made this branch's vectors
  status TEXT NOT NULL DEFAULT 'queued'
         CHECK (status IN ('queued', 'indexing', 'ready', 'failed')),
  error TEXT,                             -- why it failed, when status = 'failed'
  total_chunks INTEGER,                   -- known once chunking finishes
  indexed_at TIMESTAMPTZ,                 -- set when status becomes 'ready'
  UNIQUE (repo_id, name)
);

CREATE TABLE files (
  id SERIAL PRIMARY KEY,
  branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
  path TEXT NOT NULL,
  content TEXT NOT NULL,                  -- full text, for read_file and search_code
  UNIQUE (branch_id, path)
);

CREATE TABLE chunks (
  id SERIAL PRIMARY KEY,
  branch_id INTEGER NOT NULL REFERENCES branches(id) ON DELETE CASCADE,
  path TEXT NOT NULL,
  start_line INTEGER NOT NULL,
  end_line INTEGER NOT NULL,
  content TEXT NOT NULL,
  embedding vector(768) NOT NULL          -- nomic-embed-text returns 768 numbers
);

-- Every chat search filters by branch first.
CREATE INDEX chunks_branch_id_idx ON chunks (branch_id);
