from typing import List
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
        self.member_ids = list[int]()
        self.group_tag_ids = list[int]()
        self.channel = bool()
        self.public = bool()
        self.last_message_at = str()
        self.messages = list[Message]()
        self.mutex = threading.Lock()

        if json:
            self.parse_json(json)
    
    def parse_json(self, json):
        self.id = json["id"]
        self.name = json["name"]
        self.created_at = json["created_at"]
        self.owner_id = json["owner_id"]
        self.member_ids = json["member_ids"]
        self.group_tag_ids = json["group_tag_ids"]
        self.channel = json["channel"]
        self.public = json["public"]
        self.last_message_at = json["last_message_at"]
    
    def print_info(self):
        print(f'==== {self.name} ====')
        print("id:", self.id)
        print("created_at:", self.created_at)
        print("owner_id:", self.owner_id)
        print("member_ids:", self.member_ids)
        print("group_tag_ids:", self.group_tag_ids)
        print("channel:", self.channel)
        print("public:", self.public)
        print("last_message_at:", self.last_message_at)