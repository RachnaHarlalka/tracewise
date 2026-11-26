"""Request and response shapes for the RepoLens API. FastAPI validates requests against these
and uses them to build the /docs page."""
from pydantic import BaseModel, Field


class IndexRequest(BaseModel):
  repo_url: str = Field(examples=["https://github.com/RachnaHarlalka/tracewise"])
  branch: str | None = None  # None: use the branch in the URL, else the repo's default branch


class IndexResponse(BaseModel):
  branch_id: int
  owner: str
  repo: str
  branch: str
  status: str        # 'ready' or 'failed' (indexing is synchronous for now)
  total_chunks: int | None
  reused: bool       # True when an up-to-date index already existed and nothing was re-embedded


class ChatRequest(BaseModel):
  branch_id: int
  question: str = Field(min_length=1)
  session_id: str | None = None  # None starts a new conversation


class ChatResponse(BaseModel):
  answer: str               # includes the "Sources: ..." line added by chat_turn
  session_id: str           # send it back on the next question to keep the conversation
  prompt_tokens: int | None
  output_tokens: int | None
