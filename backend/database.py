"""
database.py — MongoDB Atlas storage layer for AI Cyber Forensic Intelligence Platform.
This file is intentionally safe: if MongoDB is unavailable, API runtime should not break.
"""
import os
import datetime
from typing import Any

import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Prefer Render environment variable. Fallback is kept for local testing.
MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://kavyakulkarni636_db_user:Reewp3XFk1zjhlme@cluster0.im2jmx0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

client = MongoClient(MONGODB_URI, server_api=ServerApi("1"), serverSelectionTimeoutMS=5000)
db = client["deepfake_forensic"]

users_collection = db["users"]
scan_history_collection = db["scan_history"]
reports_collection = db["reports"]
audit_logs_collection = db["audit_logs"]


def _clean_for_mongo(value: Any) -> Any:
    """Convert NumPy / non-serializable objects into MongoDB-safe values."""
    if isinstance(value, dict):
        return {str(k): _clean_for_mongo(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_clean_for_mongo(v) for v in value]
    if isinstance(value, tuple):
        return [_clean_for_mongo(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, datetime.datetime):
        return value
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _safe_db_call(action_name: str, func):
    try:
        return func()
    except Exception as exc:
        print(f"⚠️ MongoDB {action_name} failed: {exc}")
        return None


def test_connection():
    return _safe_db_call("connection test", lambda: client.admin.command("ping"))


def save_user(user_data: dict):
    data = _clean_for_mongo(dict(user_data))
    data["updated_at"] = datetime.datetime.now()
    username = data.get("username") or data.get("email")
    return _safe_db_call(
        "save_user",
        lambda: users_collection.update_one({"username": username}, {"$set": data}, upsert=True)
    )


def save_scan(scan_data: dict):
    data = _clean_for_mongo(dict(scan_data))
    data["created_at"] = datetime.datetime.now()
    return _safe_db_call("save_scan", lambda: scan_history_collection.insert_one(data))


def save_report(scan_id: str, report_data: dict):
    data = _clean_for_mongo(dict(report_data))
    payload = {
        "scan_id": scan_id,
        "report": data,
        "created_at": datetime.datetime.now(),
        "updated_at": datetime.datetime.now(),
    }
    return _safe_db_call(
        "save_report",
        lambda: reports_collection.update_one({"scan_id": scan_id}, {"$set": payload}, upsert=True)
    )


def save_audit_log(log_data: dict):
    data = _clean_for_mongo(dict(log_data))
    data["created_at"] = datetime.datetime.now()
    return _safe_db_call("save_audit_log", lambda: audit_logs_collection.insert_one(data))
