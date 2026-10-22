CHAT_MODEL_NAME = "llama3.2:3b"
EMBEDDING_MODEL_NAME = "nomic-embed-text"

SYSTEM_PROMPT_TEXT = """You are an assistant that answers questions about a code repository.
You will receive excerpts from the repository (the context) and a question.

Rules:
- Answer ONLY using the context. If the answer is not in the context, reply exactly: "I don't know based on the provided files."
- Answer in your own words in 1 to 3 short sentences. Do not copy or quote code or text.
- After the answer, add one line: "Sources: " followed by the file paths and line ranges you used, like README.md:1-10. Only cite files that appear in the context.

Example:
Question: How does the app send emails?
Answer: It sends emails through the SMTP client in the mailer module.
Sources: src/mailer.py:12-30

"""


SKIP_DIRS = {
    ".git", "node_modules", "dist", "build", "out", ".next", ".nuxt",
    "__pycache__", ".venv", "venv", "env", ".tox", ".mypy_cache",
    ".pytest_cache", ".ruff_cache", ".idea", ".vscode",
    "vendor", "coverage", "target", "site-packages", ".gradle",
}

SKIP_FILES = {
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "poetry.lock",
    "Pipfile.lock", "uv.lock", "Cargo.lock", "composer.lock", "go.sum",
    ".DS_Store",
}
SKIP_SUFFIXES = (".min.js", ".min.css", ".map", ".lock", ".svg", ".png", ".jpg", ".pdf")

CONSIDERED_FILE_FORMATS = (".md",".py",".ts",".js",".json")

CHUNK_SIZE = 10
CHUNK_OVERLAP = 2
