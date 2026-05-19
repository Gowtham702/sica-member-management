import firebase_admin
from firebase_admin import credentials

# Path to your service account key
# cred = credentials.Certificate("E:/Assismets/sica_addons/firebase_push_notification/data/serviceAccountKey.json")
import os
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
cred = credentials.Certificate(os.path.join(BASE_DIR, "data", "serviceAccountKey.json"))

# Initialize Firebase only if not already initialized
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred)
