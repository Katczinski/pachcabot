from typing import List

class Task:
    id:int = 0	                    # Идентификатор созданной задачи
    kind = ""	                    # Тип
    content	= ""	                # Описание
    due_at	= ""	                # Срок выполнения задачи (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    priority:int = 0	            # Приоритет
    user_id:int = 0	                # Идентификатор пользователя-создателя задачи
    status = ""	                    # Статус задачи (активная - undone)
    created_at	= ""	            # Дата и время создания задачи (ISO-8601, UTC+0) в формате YYYY-MM-DDThh:mm:ss.sssZ
    performer_ids:List[int]	= []    # Массив идентификаторов пользователей, привязанных к задаче как «ответственные»

    def __init__(self, json = {}):
        if json:
            self.parse_json(json)

    def parse_json(self, json):
        self.id = json["id"]
        self.kind = json["kind"]
        self.content = json["content"]
        self.due_at	= json["due_at"]
        self.priority = json["priority"]
        self.user_id = json["user_id"]
        self.status	= json["status"]
        self.created_at	= json["created_at"]
        self.performer_ids = json["performer_ids"]

    def _is_valid_operand(self, other):
        return (hasattr(other, "id") and
                hasattr(other, "kind") and
                hasattr(other, "content") and
                hasattr(other, "due_at") and
                hasattr(other, "priority") and
                hasattr(other, "user_id") and
                hasattr(other, "status") and
                hasattr(other, "created_at") and
                hasattr(other, "performer_ids"))
    
    def __eq__(self, other):
        if not self._is_valid_operand(other):
            return NotImplemented
        return (self.user_id == other.user_id and
                self.kind == other.kind and
                self.content == other.content and
                self.due_at == other.due_at and
                self.priority == other.priority and
                self.user_id == other.user_id and
                self.status == other.status and
                self.created_at == other.created_at and
                self.performer_ids == other.performer_ids)