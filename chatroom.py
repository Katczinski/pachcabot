import json
import threading 

class ChatRoom:
    id = 0
    name = ""
    created_at = ""
    owner_id = 0
    member_ids = []
    group_tag_ids = []
    channel = False
    public = False
    last_message_at = ""
    messages = []
    mutex = None

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)
        self.messages = []
        self.mutex = threading.Lock()
    
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
        print("=================\n")