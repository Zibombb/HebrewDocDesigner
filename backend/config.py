import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
CHROMA_DIR = DATA_DIR / "chroma"
VOICE_PROFILE_PATH = DATA_DIR / "voice_profile.json"
CONTENT_SOURCES_PATH = DATA_DIR / "content_sources.json"
BOOKS_PATH = DATA_DIR / "books.json"

# Ensure data directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "claude-opus-4-6"
MAX_CHUNK_SIZE = 800  # words per chunk
