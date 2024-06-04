from typing import List

class Message:
    id:int = 0                  # Идентификатор сообщения
    entity_type:str = ""        # Тип сущности, к которой относится сообщение: беседа/канал (discussion), тред (thread) или пользователь (user)
    entity_id:int = 0           # Идентификатор сущности, к которой относится сообщение (беседы/канала, треда или пользователя)
    chat_id:int = 0             # Идентификатор чата, в котором находится сообщение
    content:str = ""            # Текст сообщения
    user_id:int = 0             # Идентификатор пользователя, создавшего сообщение
    created_at:str = ""         # Дата и время создания сообщения (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    files:List[object] = []     # Прикреплённые файлы
    thread:object = None        # Тред сообщения. Возвращается как null, если у сообщения нет комментариев.
    parent_message_id:int = 0   # Идентификатор сообщения, к которому написан ответ. Возвращается как null, если сообщение не является ответом.

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
                # self.thread == other.thread and       # could mess up message history when thread added
                self.parent_message_id == other.parent_message_id)

    def print_info(self):
        print("=========")
        print("id", self.id)
        print("entity_type", self.entity_type)
        print("entity_id", self.entity_id)
        print("chat_id", self.chat_id)
        print("content", self.content)
        print("user_id", self.user_id)
        print("created_at", self.created_at)
        print("files", self.files)
        print("thread", self.thread)
        print("parent_message_id", self.parent_message_id)
        print("=========")


