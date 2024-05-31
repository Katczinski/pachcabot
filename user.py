import json

class User:
    id = 0
    first_name = ""
    last_name = ""
    nickname = ""
    email = ""
    phone_number = ""
    department = ""
    role = ""
    suspended = False
    invite_status = ""
    list_tags = []
    custom_properties = []
    user_status = 0
    bot = False
    created_at = ""

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)

    def parse_json(self, json):
        self.id = json["id"]
        self.first_name = json["first_name"]
        self.last_name = json["last_name"]
        self.nickname = json["nickname"]
        self.email = json["email"]
        self.phone_number = json["phone_number"]
        self.department = json["department"]
        self.role = json["role"]
        self.suspended = json["suspended"]
        self.invite_status = json["invite_status"]
        self.list_tags = json["list_tags"]
        self.custom_properties = json["custom_properties"]
        self.user_status = json["user_status"]
        self.bot = json["bot"]
        self.created_at = json["created_at"]