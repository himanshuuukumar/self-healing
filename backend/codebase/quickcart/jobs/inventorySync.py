import os

# Intentional bug: missing env var
# The logs say KeyError: 'INVENTORY_API_URL'
INVENTORY_API_URL = os.environ["INVENTORY_API_URL"]

def sync_inventory():
    print(f"Syncing with {INVENTORY_API_URL}")
