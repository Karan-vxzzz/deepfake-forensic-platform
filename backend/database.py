import os
from pymongo import MongoClient

MONGODB_URI = os.getenv("MONGODB_URI")

client = MongoClient(MONGODB_URI)

db = client["deepfake_forensic_db"]

users_collection = db["users"]
scan_history_collection = db["scan_history"]
reports_collection = db["reports"]
audit_logs_collection = db["audit_logs"]