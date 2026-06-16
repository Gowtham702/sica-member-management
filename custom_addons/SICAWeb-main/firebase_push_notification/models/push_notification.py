import firebase_admin
from firebase_admin import credentials, messaging
import os
import logging

_logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

firebase_file = os.path.join(
    BASE_DIR,
    "data",
    "serviceAccountKey.json"
)

# Initialize Firebase only if JSON file exists
if os.path.exists(firebase_file):
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_file)
            firebase_admin.initialize_app(cred)
            _logger.info("Firebase initialized successfully")
    except Exception as e:
        _logger.error("Firebase initialization failed: %s", str(e))
else:
    _logger.warning(
        "Firebase disabled. serviceAccountKey.json not found at: %s",
        firebase_file
    )