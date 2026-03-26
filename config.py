import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "data", "emotions.db")
DEFAULT_LANGUAGE = "de"
SUPPORTED_LANGUAGES = ["de", "en"]
APP_TITLE = "DAFEU - Digitaler Assistent für emotionale Unterstützung"
APP_VERSION = "0.1.0"
WINDOW_WIDTH = 600
WINDOW_HEIGHT = 700
