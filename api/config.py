from pathlib import Path


# Base directories
API_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = API_DIR.parents[1]


# Model artifacts
MODEL_ROOT = API_DIR / "models" / "ssl_alphabet"
MODEL_PATH = MODEL_ROOT / "ssl_alphabet_lstm.keras"
SCALER_PATH = MODEL_ROOT / "ssl_alphabet_lstm_scaler.pkl"
META_PATH = MODEL_ROOT / "ssl_alphabet_sequences.pkl"


# Feature / sequence configuration (matches training)
N_FEATS = 63  # 1 hand × 21 landmarks × 3 coords
NUM_LANDMARKS = 21
COORDS_PER_LM = 3

# Default sequence length (can be overridden by metadata)
DEFAULT_SEQ_LEN = 30


# HTML helper pages
HTML_DIR = API_DIR / "html"
WEBCAM_HTML_PATH = HTML_DIR / "webcam.html"
LETTERS_HTML_PATH = HTML_DIR / "letters.html"
MULTI_WEBCAM_HTML_PATH = HTML_DIR / "multi_webcam.html"
MULTI_CLASSES_HTML_PATH = HTML_DIR / "multi_classes.html"

