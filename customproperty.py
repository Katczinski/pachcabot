from typing import Any
import json as Json

class CustomProperty:
    id:int = 0          # Идентификатор поля
    name:str = ""       # Название поля
    data_type:str = ""  # Тип поля (string, number, date или link)
    value:Any ; None

    def __init__(self, json = {}):
        if json:
            self.from_json(json)

    def from_json(self, json):
        print("from json in cp")
        self.id = json["id"]
        self.name = json["name"]
        self.data_type = json["data_type"]
        self.value = json["value"] if "value" in json else None

    def to_json(self):
        return Json.loads(Json.dumps(
            self,
            default=lambda o: o.__dict__, 
            sort_keys=False,
            indent=4))

    def _is_valid_operand(self, other):
        return (hasattr(other, "id") and
                hasattr(other, "name") and
                hasattr(other, "data_type") and
                hasattr(other, "value"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.id == other.id and
                self.name == other.name and
                self.data_type == other.data_type and
                self.value == other.value) # ??
    
    def print_info(self, str=""):
        print(str, self.to_json())