from typing import Any

class CustomProperty:
    id:int = 0          # Идентификатор поля
    name:str = ""       # Название поля
    data_type:str = ""  # Тип поля (string, number, date или link)
    value:Any ; None

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)

    def parse_json(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.data_type = json["data_type"]
        self.value = json["value"]

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