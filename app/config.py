import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Data directories
DATA_DIR = PROJECT_ROOT / "data"
VECTORSTORE_DIR = PROJECT_ROOT / "vectorstore"

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# Create directories if they don't exist
DATA_DIR.mkdir(exist_ok=True)
VECTORSTORE_DIR.mkdir(exist_ok=True)

