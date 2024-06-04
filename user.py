from typing import List
from customproperty import CustomProperty

class User:
    id:int = 0                          # Идентификатор пользователя
    first_name:str = ""                 # Имя
    last_name:str = ""                  # Фамилия
    nickname:str = ""                   # Имя пользователя
    email:str = ""                      # Электронная почта
    phone_number:str = ""               # Телефон
    department:str = ""                 # Подразделение
    role:str = ""                       # Уровень доступа: admin (администратор), user (сотрудник), multi_guest (мульти-гость)
    suspended:bool = False              # Приостановка доступа
    invite_status:str = ""              # Статус пришлашения: confirmed (принято), sent (отправлено)
    list_tags:List[str] = []            # Массив тегов, привязанных к сотруднику
    custom_properties:List[CustomProperty] = [] # Дополнительные поля сотрудника
    user_status:object = None           # Статус. Возвращается как null, если статус не установлен.
    bot:bool = False                    # Тип: пользователь (false) или бот (true)
    created_at:str = ""                 # Дата создания (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ

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
        for property_json in json["custom_properties"]:
            self.custom_properties.append(CustomProperty(property_json))
        self.user_status = json["user_status"]
        self.bot = json["bot"]
        self.created_at = json["created_at"]
    
    def print_info(self):
        print("id:", self.id)
        print("first_name:", self.first_name)
        print("last_name:", self.last_name)
        print("nickname:", self.nickname)
        print("email:", self.email)
        print("phone_number:", self.phone_number)
        print("department:", self.department)
        print("role:", self.role)
        print("suspended:", self.suspended)
        print("invite_status:", self.invite_status)
        print("list_tags:", self.list_tags)
        print("custom_properties:", self.custom_properties)
        print("user_status:", self.user_status)
        print("bot:", self.bot)
        print("created_at:", self.created_at)
        print("============================")