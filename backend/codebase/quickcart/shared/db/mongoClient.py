from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError

def get_client(mongo_uri: str):
    # Intentional bug: bad URI or no timeout config
    try:
        _client = MongoClient(mongo_uri)
        # Force connection check
        _client.admin.command('ping')
    except ServerSelectionTimeoutError:
        # Logs say: pymongo.errors.ServerSelectionTimeoutError
        raise
