# DB config & settings
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
UPLOAD_DIR = "uploads"