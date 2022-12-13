
import json
class BotConfig:


    def __init__(self, filename: str):
        self.filename = filename


    def set(self, serverID: int, key: str, value: int, relative = False):
        try:
            with open(self.filename,'r') as file:
                file_data = json.load(file)
            
            with open(self.filename,'w') as file:
                # server is known, add new dict key
                if str(serverID) in file_data.keys():
                    if key in file_data[str(serverID)].keys() and relative: 
                        file_data[str(serverID)][key] += value
                    else: 
                        file_data[str(serverID)][key] = value
                # server never made key before, add new entry for server
                else:
                    file_data[str(serverID)] = {key: value}
                # dump changes to json file
                json.dump(file_data, file, indent = 4)
        except:
            # cfg file empty / did not exist, make first entry
            with open(self.filename, "w") as file:
                json.dump({serverID : {key: value}}, file, indent = 4)
    

    # gets the value for a key in a given server if it exists
    def get(self, serverID: int, key: str):
        try:
            with open(self.filename,'r') as file:
                file_data = json.load(file)
                return file_data[str(serverID)][key]
        except:
            return None


    # removes the setting entry for a server
    def clear(self, serverID: int, key: str):
        try:
            with open(self.filename,'r') as file:
                file_data = json.load(file)
                
            with open(self.filename,'w') as file:
                del file_data[str(serverID)][key]
                json.dump(file_data, file, indent = 4)
            return True
        except:
            return False
        
    # returns the highest key value for the server
    def max_key(self, serverID: int):
        try:
            with open(self.filename, 'r') as file:
                file_data = json.load(file)
                return max(file_data[str(serverID)], key=file_data[str(serverID)].get)
        except:
            return None
    
    def sorted_list(self, serverID: int):
        try:
            with open(self.filename, 'r') as file:
                file_data = json.load(file)
                return sorted(file_data[str(serverID)].items(), key=lambda points: points[1], reverse=True)
        except:
            return None
    
        

