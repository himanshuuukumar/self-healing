import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import logging

logger = logging.getLogger(__name__)

# BUG: No connection pool limit set, no reconnect logic, no timeout configured
# Under heavy load this will exhaust connections silently
_client = None

def get_client():
    global _client
    if _client is None:
        mongo_uri = os.environ.get("MONGO_URI")  
        # BUG: No fallback if MONGO_URI is not set — will crash with TypeError
        _client = MongoClient(mongo_uri)
    return _client

def get_db(db_name="quickcart"):
    client = get_client()
    return client[db_name]

def get_collection(collection_name):
    db = get_db()
    return db[collection_name]

def ping():
    try:
        client = get_client()
        client.admin.command("ping")
        return True
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"MongoDB ping failed: {e}")
        return False
