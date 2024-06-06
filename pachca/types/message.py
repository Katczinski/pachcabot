from typing import List
import json as Json

class Message:
    id:int                  # Идентификатор сообщения
    entity_type:str         # Тип сущности, к которой относится сообщение: беседа/канал (discussion), тред (thread) или пользователь (user)
    entity_id:int           # Идентификатор сущности, к которой относится сообщение (беседы/канала, треда или пользователя)
    chat_id:int             # Идентификатор чата, в котором находится сообщение
    content:str             # Текст сообщения
    user_id:int             # Идентификатор пользователя, создавшего сообщение
    created_at:str          # Дата и время создания сообщения (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    files:List[object]      # Прикреплённые файлы
    thread:object           # Тред сообщения. Возвращается как null, если у сообщения нет комментариев.
    parent_message_id:int   # Идентификатор сообщения, к которому написан ответ. Возвращается как null, если сообщение не является ответом.

    def __init__(self, json = {}):
        self.id = int()
        self.entity_type = str()
        self.entity_id = int()
        self.chat_id = int()
        self.content = str()
        self.user_id = int()
        self.created_at = str()
        self.files = []
        self.thread = object()
        self.parent_message_id = int()

        if json:
            self.from_json(json)
    
    def from_json(self, json):
        self.id = json["id"]
        self.entity_type = json["entity_type"]
        self.entity_id = json["entity_id"]
        self.chat_id = json["chat_id"]
        self.content = json["content"]
        self.user_id = json["user_id"]
        self.thread = json["thread"] 
        if "files" in json: self.files = json["files"]
        if "created_at" in json: self.created_at = json["created_at"]
        if "parent_message_id" in json: self.parent_message_id = json["parent_message_id"]
        
        

    def to_json(self):
        return Json.loads(Json.dumps(
            self,
            default=lambda x: getattr(x, '__dict__', str(x)),
            sort_keys=False,
            indent=4))
    
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
        return (self.id == other.id and                     #   +
                self.entity_type == other.entity_type and   #   +
                self.entity_id == other.entity_id and       #   +
                self.chat_id == other.chat_id and           #   +
                self.content == other.content and           #
                self.user_id == other.user_id and           #   +
                self.created_at == other.created_at)        #   +
                # self.files == other.files and             #         # messages to be deleted do not have this field
                # self.thread == other.thread and           #         # could mess up message history when thread added // TODO: Check this again
                # self.parent_message_id == other.parent_message_id)  # messages to be deleted do not have this field
    
    def print_info(self, str=""):
        print(str, self.to_json())


