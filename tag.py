
class Tag:
    id:int = 0              # Идентификатор тега
    name:str = ""           # Название тега
    users_count:int = 0     # Количество сотрудников, которые имеют этот тег

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)

    def parse_json(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.users_count = json["users_count"]

    def _is_valid_operand(self, other):
        return (hasattr(other, "id") and
                hasattr(other, "name") and
                hasattr(other, "users_count"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.id == other.id and
                self.name == other.name and
                self.users_count == other.users_count)
