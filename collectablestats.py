# collectablestats.py

import json
import os
import asyncio

class CollectionStats:
    def __init__(self, filename: str):
        self.filename = filename
        self.lock = asyncio.Lock()

    # load data from the JSON file
    async def _load_data(self):
        async with self.lock:
            if not os.path.exists(self.filename):
                return {}
            # thread pool to handle blocking I/O
            loop = asyncio.get_event_loop()
            try:
                with open(self.filename, 'r') as file:
                    data = await loop.run_in_executor(None, json.load, file)
                return data
            except json.JSONDecodeError:
                return {}

    # save data to the JSON file
    async def _save_data(self, data):
        async with self.lock:
            loop = asyncio.get_event_loop()
            # thread pool to handle blocking I/O
            await loop.run_in_executor(None, self._write_json, data)

    def _write_json(self, data):
        with open(self.filename, 'w') as file:
            json.dump(data, file, indent=4)

    # add a discord userID to an item's owner list for a specific server
    async def add_user_to_item(self, serverID: str, itemID: str, userID: str):
        data = await self._load_data()
        server_data = data.setdefault(serverID, {})
        user_list = server_data.setdefault(itemID, [])
        if userID not in user_list:
            user_list.append(userID)
            await self._save_data(data)
            return True  # success adding user to item
        else:
            return False  # fail if user already own item

    # remove a userID from an item's owner list for a specific server
    async def remove_user_from_item(self, serverID: str, itemID: str, userID: str):
        data = await self._load_data()

        try:
            user_list = data[serverID][itemID]
            if userID in user_list:
                user_list.remove(userID)
                if not user_list:
                    # remove item id entry if no one owns item
                    del data[serverID][itemID]
                    if not data[serverID]:
                        # no data for server, delete server id from log
                        del data[serverID]
                await self._save_data(data)
                return True  # user removed from item success
            else:
                return False  # case doesnt own item
        except KeyError:
            return False  # item or server doesnt exist
        

    # returns the LIST OF USERIDS who own an item in a specific server
    async def get_users_for_item(self, serverID: str, itemID: str):
        data = await self._load_data()
        return data.get(serverID, {}).get(itemID, [])


    # returns NUMBER OF USERS who own an item in a specific server
    async def count_users_for_item(self, serverID: str, itemID: str):
        users = await self.get_users_for_item(serverID, itemID)
        return len(users)

    # returns all items owned by a user in a specific server
    async def get_items_for_user(self, serverID: str, userID: str):
        data = await self._load_data()
        server_data = data.get(serverID, {})
        items = [itemID for itemID, users in server_data.items() if userID in users]
        return items
