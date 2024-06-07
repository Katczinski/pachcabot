from typing import List
from .customproperty import CustomProperty
import json as Json

class User:
    id:int                                  # Идентификатор пользователя
    first_name:str                          # Имя
    last_name:str                           # Фамилия
    nickname:str                            # Имя пользователя
    email:str                               # Электронная почта
    phone_number:str                        # Телефон
    department:str                          # Подразделение
    role:str                                # Уровень доступа: admin (администратор), user (сотрудник), multi_guest (мульти-гость)
    suspended:bool                          # Приостановка доступа
    invite_status:str                       # Статус пришлашения: confirmed (принято), sent (отправлено)
    list_tags:List[str]                     # Массив тегов, привязанных к сотруднику
    custom_properties:List[CustomProperty]  # Дополнительные поля сотрудника
    user_status:object                      # Статус. Возвращается как null, если статус не установлен.
    bot:bool                                # Тип: пользователь (false) или бот (true)
    created_at:str                          # Дата создания (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ

    def __init__(self, json = {}):
        self.id = int()
        self.first_name = str()
        self.last_name = str()
        self.nickname = str()
        self.email = str()
        self.phone_number = str()
        self.department = str()
        self.role = str()
        self.suspended = bool()
        self.invite_status = str()
        self.list_tags = []
        self.custom_properties = []
        self.user_status = object()
        self.bot = bool()
        self.created_at = str()
    
        if json:
            self.from_json(json)

    def _is_valid_operand(self, other):
        return (hasattr(other, "id") and
                hasattr(other, "first_name") and
                hasattr(other, "last_name") and
                hasattr(other, "nickname") and
                hasattr(other, "email") and
                hasattr(other, "phone_number") and
                hasattr(other, "department") and
                hasattr(other, "role") and
                hasattr(other, "suspended") and
                hasattr(other, "invite_status") and
                hasattr(other, "list_tags") and
                hasattr(other, "custom_properties") and
                hasattr(other, "user_status") and
                hasattr(other, "bot") and
                hasattr(other, "created_at"))

    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.id == other.id)     

    def from_json(self, json):
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

    def to_json(self):
        return Json.loads(Json.dumps(
            self,
            default=lambda x: getattr(x, '__dict__', str(x)),
            sort_keys=False,
            indent=4))

    def print_info(self, str=""):
        print(str, self.to_json())

    # def print_info(self):
    #     print("id:", self.id)
    #     print("first_name:", self.first_name)
    #     print("last_name:", self.last_name)
    #     print("nickname:", self.nickname)
    #     print("email:", self.email)
    #     print("phone_number:", self.phone_number)
    #     print("department:", self.department)
    #     print("role:", self.role)
    #     print("suspended:", self.suspended)
    #     print("invite_status:", self.invite_status)
    #     print("list_tags:", self.list_tags)
    #     print(f'custom_properties[{len(self.custom_properties)}]:')
    #     [p.print_info("     ") for p in self.custom_properties]
    #     print("user_status:", self.user_status)
    #     print("bot:", self.bot)
    #     print("created_at:", self.created_at)
    #     print("============================")