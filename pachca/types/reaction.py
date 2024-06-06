import json as Json

class Reaction:
    user_id:int     # Идентификатор пользователя, который добавил реакцию
    created_at:str  # Дата и время добавления реакции (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    code:str        # Emoji символ реакции
    message_id:int

    def __init__(self, json = {}):
        self.user_id = int()
        self.created_at = str()
        self.code = str()
        self.message_id = int()

        if json:
            self.from_json(json)

    def from_json(self, json):
        self.user_id = json["user_id"]
        self.code = json["code"]
        if "created_at" in json: self.created_at = json["created_at"]
        if "message_id" in json: self.message_id = json["message_id"]

    def to_json(self):
        return Json.loads(Json.dumps(
            self,
            default=lambda x: getattr(x, '__dict__', str(x)),
            sort_keys=False,
            indent=4))

    def _is_valid_operand(self, other):
        return (hasattr(other, "user_id") and
                hasattr(other, "created_at") and
                hasattr(other, "code"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.user_id == other.user_id and
                self.created_at == other.created_at and
                self.code == other.code)
    
    def print_info(self, str=""):
        print(str, self.to_json())