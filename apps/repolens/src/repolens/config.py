MODEL_NAME = "llama3.2:3b"

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
