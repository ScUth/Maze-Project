import json

class Config_json:
    def __init__(self, file_path):
        self.file_path = file_path
        self.db = None
    
    def _load_json(self):
        with open(self.file_path, "r") as f:
            self.db = json.load(f)
            
    def _save_json(self):
        with open(self.file_path, "w") as f:
            json.dump(self.db, f)
            
    def _get_data(self, table, key):
        # print(self.db[table][0][key])
        return self.db[table][0][key]
    
    
# cj = Config_json("config.json")
# cj._load_json()
# cj._get_data("WINDOWS", "height")