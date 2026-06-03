import os
import datetime
from pymongo import MongoClient
from pymongo.server_api import ServerApi

MONGODB_URI = os.getenv(
    "MONGODB_URI",
    "mongodb+srv://kavyakulkarni636_db_user:Reewp3XFk1zjhlme@cluster0.im2jmx0.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
)

mongodb_enabled = False

try:
    client = MongoClient(MONGODB_URI, server_api=ServerApi("1"))
    client.admin.command("ping")

    db = client["deepfake_forensic"]

    users_collection = db["users"]
    reports_collection = db["reports"]
    scan_history_collection = db["scan_history"]
    audit_logs_collection = db["audit_logs"]

    mongodb_enabled = True
    print("✅ Connected to MongoDB Atlas")

except Exception as e:
    print(f"⚠️ MongoDB storage disabled: {e}")

    client = None
    db = None
    users_collection = None
    reports_collection = None
    scan_history_collection = None
    audit_logs_collection = None


def save_user(user_data: dict):
    if users_collection is None:
        return None

    data = dict(user_data)
    data["updated_at"] = datetime.datetime.now()

    return users_collection.update_one(
        {"username": data.get("username")},
        {"$set": data},
        upsert=True
    )


def save_report(scan_id: str, report_data: dict):
    if reports_collection is None:
        return None

    data = {
        "scan_id": scan_id,
        "report": report_data,
        "created_at": datetime.datetime.now()
    }

    return reports_collection.update_one(
        {"scan_id": scan_id},
        {"$set": data},
        upsert=True
    )


def save_scan(scan_data: dict):
    if scan_history_collection is None:
        return None

    data = dict(scan_data)
    data["created_at"] = datetime.datetime.now()

    return scan_history_collection.insert_one(data)


def save_audit_log(log_data: dict):
    if audit_logs_collection is None:
        return None

    data = dict(log_data)
    data["created_at"] = datetime.datetime.now()

    return audit_logs_collection.insert_one(data)