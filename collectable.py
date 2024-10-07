# collectable.py

import json
from util import bot_directory


# this is just to represent items in user inventories

class Item:
    def __init__(self, item_id, name, description, itemclass, 
        rarity='common', 
        edible=False, 
        smokeable=False, 
        injectable=False, 
        snortable=False
    ):
        self.item_id = item_id      
        self.name = name            
        self.description = description  
        self.itemclass = itemclass
        self.rarity = rarity
        self.edible = edible
        self.smokeable = smokeable
        self.injectable = injectable
        self.snortable = snortable

    def __repr__(self):
        return f"Item({self.item_id}, {self.name}, Class={self.itemclass})"


def load_items(json_file_path): 
    try:
        with open(json_file_path, 'r') as file:
            items_data = json.load(file)
    except FileNotFoundError:
        print(f"Error: The file {json_file_path} does not exist.")
        return {}
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON: {e}")
        return {}
    
    items = {}
    for item_id, attributes in items_data.items():
        # extract mandatory attributes
        item_id = attributes.get('item_id')
        name = attributes.get('name')
        description = attributes.get('description')
        itemclass = attributes.get('itemclass')
        
        if not all([item_id, name, description, itemclass]):
            print(f"Skipping item '{item_id}' due to missing mandatory attributes.")
            continue
        
        # extract optional attributes with defaults
        rarity = attributes.get('rarity', 'common')
        edible = attributes.get('edible', False)
        smokeable = attributes.get('smokeable', False)
        injectable = attributes.get('injectable', False)
        snortable = attributes.get('snortable', False)
        
        # create an Item instance
        item = Item(
            item_id=item_id,
            name=name,
            description=description,
            itemclass=itemclass,
            rarity=rarity,
            edible=edible,
            smokeable=smokeable,
            injectable=injectable,
            snortable=snortable
        )
        
        items[item_id] = item
    
    return items

# just lists all the items in the json for test purpose
if __name__ == "__main__":
    items = load_items(f"{bot_directory}resources/storage/items.json")
    for item_id, item in items.items():
        print(item)
