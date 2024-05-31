import json

class Message:
    id = 0
    entity_type = ""
    entity_id = 0
    chat_id = 0
    content = ""
    user_id = 0
    created_at = ""
    files = []
    thread = []
    parent_message_id = 0

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)
    
    def parse_json(self, json):
        self.id = json["id"]
        self.entity_type = json["entity_type"]
        self.entity_id = json["entity_id"]
        self.chat_id = json["chat_id"]
        self.content = json["content"]
        self.user_id = json["user_id"]
        self.created_at = json["created_at"]
        self.files = json["files"]
        self.thread = json["thread"]
        self.parent_message_id = json["parent_message_id"]

    def _is_valid_operand(self, other):
        return (hasattr(other, "id") and
                hasattr(other, "entity_type") and
                hasattr(other, "entity_id") and
                hasattr(other, "chat_id") and
                hasattr(other, "content") and
                hasattr(other, "user_id") and
                hasattr(other, "created_at") and
                hasattr(other, "files") and
                hasattr(other, "thread") and
                hasattr(other, "parent_message_id"))

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.id == other.id and
                self.entity_type == other.entity_type and
                self.entity_id == other.entity_id and
                self.chat_id == other.chat_id and
                self.content == other.content and
                self.user_id == other.user_id and
                self.created_at == other.created_at and
                self.files == other.files and
                self.thread == other.thread and
                self.parent_message_id == other.parent_message_id)


