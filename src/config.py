import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

DATABASE_URL: str = os.getenv("DATABASE_URL")
BASE_DIR = Path(__file__).parent.parent
STATIC_DIR = os.path.join(BASE_DIR, "static")

