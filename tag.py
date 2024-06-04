import json as Json

class Tag:
    id:int              # Идентификатор тега
    name:str            # Название тега
    users_count:int     # Количество сотрудников, которые имеют этот тег

    def __init__(self, json = {}):
        self.id = int()
        self.name = str()
        self.users_count = int()

        if json:
            self.from_json(json)

    def from_json(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.users_count = json["users_count"]

    def to_json(self):
        return Json.loads(Json.dumps(
            self,
            default=lambda x: getattr(x, '__dict__', str(x)),
            sort_keys=False,
            indent=4))

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
    
    def print_info(self, str=""):
        print(str, self.to_json())