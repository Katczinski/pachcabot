from __future__ import annotations
from typing import List
import json as Json
import threading 

from message import Message

class ChatRoom:
    id:int                      # Идентификатор беседы или канала
    name:str                    # Название
    owner_id:int                # Идентификатор пользователя, создавшего беседу или канал
    created_at:str              # Дата и время создания беседы или канала (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    member_ids:List[int]        # Массив идентификаторов пользователей, участников
    group_tag_ids:List[int]     # Массив идентификаторов тегов, участников
    channel:bool                # Тип: беседа (false) или канал (true)
    public:bool                 # Доступ: закрытый (false) или открытый (true)
    last_message_at:str         # Дата и время создания последнего сообщения в беседе/калане (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    messages:List[Message]      # Кэш последних сообщений
    mutex:threading.Lock        # Мьютекс

    def __init__(self, json = {}):
        self.id = int()
        self.name = str()
        self.owner_id = int()
        self.created_at = str()
        self.member_ids = []
        self.group_tag_ids = []
        self.channel = bool()
        self.public = bool()
        self.last_message_at = str()
        self.messages = []
        self.mutex = threading.Lock()

        if json:
            self.from_json(json)
    
    def from_json(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.created_at = json["created_at"]
        self.owner_id = json["owner_id"]
        self.member_ids = json["member_ids"]
        self.group_tag_ids = json["group_tag_ids"]
        self.channel = json["channel"]
        self.public = json["public"]
        self.last_message_at = json["last_message_at"]

    def to_json(self):
        return Json.loads(Json.dumps(
            self,
            default=lambda x: getattr(x, '__dict__', str(x)), 
            sort_keys=False,
            indent=4))

    def print_info(self, str=""):
        print(str, self.to_json())