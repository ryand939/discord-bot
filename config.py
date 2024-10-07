# config.py

import json
import asyncio

# Simple config system that stores a dictionary for each individual server

class BotConfig:

    def __init__(self, filename: str):
        self.filename = filename
        self.lock = asyncio.Lock()

        
    def _read_json(self):
        with open(self.filename, 'r') as file:
            return json.load(file)

    def _write_json(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)


    # set a value for a key in a server
    async def set(self, serverID: str, key: str, value: int, relative=False):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
            except (FileNotFoundError, json.JSONDecodeError):
                file_data = {}
            
            # server is known, add/update key
            if serverID in file_data:
                if key in file_data[serverID] and relative: 
                    file_data[serverID][key] += value
                else: 
                    file_data[serverID][key] = value
            # server never made key before, add new entry for server
            else:
                file_data[serverID] = {key: value}

            # dump changes to JSON file
            await loop.run_in_executor(None, self._write_json, file_data)
    

    # gets the value for a key in a given server if it exists
    async def get(self, serverID: str, key: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
                return file_data[serverID][key]
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return None

    # removes the setting entry for a server
    async def clear(self, serverID: str, key: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
                if key not in file_data[serverID]:
                    return False
                del file_data[serverID][key]
                await loop.run_in_executor(None, self._write_json, file_data)
                return True
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return False
        
    # returns the key with the highest value for the server
    async def max_key(self, serverID: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
                # filter out inventory keys
                balances = {
                    key: value 
                    for key, value in file_data[serverID].items() 
                    if not key.startswith('inventory_') and isinstance(value, (int, float))
                }
                if not balances:
                    return None
                return max(balances, key=balances.get)
            except (FileNotFoundError, json.JSONDecodeError, KeyError, ValueError):
                return None



    async def get_list(self, serverID: str = None, sort=False):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
                if serverID is None:
                    return file_data
                # filter out inventory keys
                balances = {
                    key: value 
                    for key, value in file_data[serverID].items() 
                    if not key.startswith('inventory_') and isinstance(value, (int, float))
                }
                if sort:
                    return sorted(balances.items(), key=lambda item: item[1], reverse=True)
                else:
                    return list(balances.items())
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return None

    # --- Inventory Management Methods ---

    # adds an item to a user's inventory (ensures uniqueness)
    async def add_to_inventory(self, serverID: str, userID: str, item: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
            except (FileNotFoundError, json.JSONDecodeError):
                file_data = {}

            # ensure server data exists
            if serverID not in file_data:
                file_data[serverID] = {}

            inventory_key = f"inventory_{userID}"

            # get or create the user's inventory list
            inventory = file_data[serverID].get(inventory_key, [])

            # add the item to the inventory if not already present
            if item not in inventory:
                inventory.append(item)
                file_data[serverID][inventory_key] = inventory
                await loop.run_in_executor(None, self._write_json, file_data)
                return True
            else:
                # case item already in inventory
                return False

    # removes an item from a user's inventory
    async def remove_from_inventory(self, serverID: str, userID: str, item: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
            except (FileNotFoundError, json.JSONDecodeError):
                return False

            inventory_key = f"inventory_{userID}"

            try:
                inventory = file_data[serverID][inventory_key]
                inventory.remove(item)
                file_data[serverID][inventory_key] = inventory

                await loop.run_in_executor(None, self._write_json, file_data)
                return True
            except (KeyError, ValueError):
                return False

    # gets the user's inventory (list of itemid strings)
    async def get_inventory(self, serverID: str, userID: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
                inventory_key = f"inventory_{userID}"
                return file_data[serverID].get(inventory_key, [])
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return []

    # clears the user's inventory
    async def clear_inventory(self, serverID: str, userID: str):
        async with self.lock:
            loop = asyncio.get_event_loop()
            try:
                file_data = await loop.run_in_executor(None, self._read_json)
                inventory_key = f"inventory_{userID}"
                if inventory_key in file_data[serverID]:
                    del file_data[serverID][inventory_key]
                    await loop.run_in_executor(None, self._write_json, file_data)
                    return True
                else:
                    return False
            except (FileNotFoundError, json.JSONDecodeError, KeyError):
                return False
