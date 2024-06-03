import json

class Reaction:
    user_id = 0
    created_at = ""
    code = ""

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)

    def parse_json(self, json):
        self.user_id = json["user_id"]
        self.created_at = json["created_at"]
        self.code = json["code"]

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