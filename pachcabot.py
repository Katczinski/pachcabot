import threading 
import time
import sys
import os
import queue
import datetime
import functools
import filetype as Filetype
from typing import List
from typing import Callable
from typing import Dict
from typing import Any
import json as Json

import pachcarequests
from chatroom import ChatRoom
from message import Message
from user import User
from file import File
from task import Task
from reaction import Reaction
from tag import Tag
from customproperty import CustomProperty

#for debug purposes
BLACKLISTED_ROOMS = []

class TaskHandle:
    name = ""
    thread = None

    def __init__(self, name="", thread=None):
        self.name = name
        self.thread = thread
    
    def set_name(self, name):
        self.name = name
    
    def set_thread(self, thread):
        self.thread = thread

class PachcaBot:
    AUTH_TOKEN:str
    API_URL = "https://api.pachca.com/api/shared/v1"
    cache_size:int
    refresh_rate:int
    _my_rooms:List[ChatRoom]
    _headers:object
    _sys_tasks:List[TaskHandle]
    _event_handlers:Dict[str, Callable]
    _new_msg_queue:queue.Queue

    uploads:List[File] # unused
    
    # init:
    # Arguments:
    #   cache_size:     Размер кэша для массива сообщений каждой комнаты. 0 - Без ограничений
    #   refresh_rate:   Период обновления новых сообщений в секундах
    # Return value:
    #   None
    def __init__(self, auth_token, cache_size=0, refresh_rate=2):
        self.AUTH_TOKEN = auth_token
        self.cache_size = cache_size
        self.refresh_rate = refresh_rate
        self._my_rooms = []
        self._new_msg_queue = queue.Queue()
        self._sys_tasks = []
        self.uploads = []
        self._event_handlers = {}
        self._headers = {
            'Authorization': f'Bearer {self.AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

        self.__chatrooms_init()
        self.__task_init_sys()

    # custom_properties_get:
    # Arguments:
    #   None
    # Return value:
    #   array of customproperty.CustomProperty: Массив дополнительных полей
    def custom_properties_get(self) -> List[CustomProperty]:
        url = f'/custom_properties?entity_type=User'

        customproperty_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)

        if not customproperty_json["data"]:
            return []
        
        properties = []
        for property_json in customproperty_json["data"]:
            property = CustomProperty(property_json)
            properties.append(property)

        return properties


    # task_create:
    # Arguments:
    #   kind:           Тип. call (позвонить контакту), meeting (встреча), reminder (напоминание), event (событие), email (написать письмо)
    #   content:        Описание.
    #   due_at:         Срок выполнения задачи. timezone aware!! e.g. datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    #   priority:       Приоритет. 1 (по умолчанию), 2 (важно) или 3 (очень важно)
    #   performer_ids:  Массив идентификаторов пользователей, привязываемых к задаче как «ответственные»
    # Return value:
    #   object task.Task 
    def task_create(self, kind, content, due_at:datetime.datetime, priority, performer_ids:List[int]) -> Task:
        url = f'/tasks'
        json = {
            "task": {
                "kind": kind,
                "content": content,
                "due_at": due_at.isoformat(),
                "priority": priority,
                "performer_ids": performer_ids
            }
        }
        task_json = pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)
        if not task_json["data"]:
            return {}
        return Task(task_json["data"])

    # user_create:
    # Arguments:   
    #   first_name:	        Имя
    #   last_name:	        Фамилия
    #   nickname:	        Имя пользователя
    #   email:		        Электронная почта
    #   phone_number:	    Телефон
    #   department:         Подразделение
    #   role:               Уровень доступа: admin (администратор), user (сотрудник), multi_guest (мульти-гость)
    #   suspended:          Приостановка доступа
    #   list_tags:          Массив тегов, привязываемых к сотруднику
    #   custom_properties:  Задаваемые дополнительные поля
    #   skip_email_notify:  Пропуск этапа отправки приглашения сотруднику (при значении true сотруднику не будет отправлено письмо на электронную почту с приглашением создать аккаунт). Данный параметр полезен в случае предварительного создания аккаунтов сотрудникам перед их входом через SSO.
    # Return value:
    #   object user.User: Созданный сотрудник
    def user_create(self,
                    first_name:str,
                    last_name:str,
                    email:str,
                    nickname:str="",
                    phone_number:str="",
                    department:str="",
                    role:str="user",
                    suspended:bool=False,
                    list_tags:List[str]=None,
                    custom_properties:List[CustomProperty]=None,
                    skip_email_notify:bool=False) -> User:
        if list_tags is None:
            list_tags = []
        if custom_properties is None:
            custom_properties = []
        url = "/users"
        json = {
            "user": {
                "first_name": first_name,
                "last_name": last_name,
                "email": email,
                "nickname": nickname,
                "phone_number": phone_number,
                "department": department,
                "role": role,
                "suspended": suspended,                
                "list_tags": [],
                "custom_properties": []
            },
            "skip_email_notify": skip_email_notify
        }
        for tag in list_tags:
            json["user"]["list_tags"].append(tag)
        for property in custom_properties:
            json["user"]["custom_properties"].append(property.to_json())

        user_json = pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)

        if not user_json["data"]:
            return {}
        return User(user_json["data"])

    # user_delete:
    # Arguments:
    #   user_id        Идентификатор пользователя
    # Return value:
    #   object Json:   При безошибочном выполнении запроса тело ответа отсутствует
    def user_delete(self, user_id:int) -> Json:
        url = f'/users/{user_id}'
        return pachcarequests.send_delete_request(self.API_URL + url, self._headers)

    # user_edit:
    # Arguments:
    #   user_id             Идентификатор пользователя
    #   first_name:	        Новое имя
    #   last_name:	        Новая фамилия
    #   nickname:	        Новое им пользователя
    #   email:		        Новая электронная почта
    #   phone_number:	    Новый телефон
    #   department:         Новое подразделение
    #   role:               Новый уровень доступа: admin (администратор), user (сотрудник), multi_guest (мульти-гость)
    #   suspended:          Новое значение приостановки доступа
    #   list_tags:          Новый массив тегов, привязываемых к сотруднику
    #   custom_properties:  Новые задаваемые дополнительные поля
    #   skip_email_notify:  Новое значение пропускф этапа отправки приглашения сотруднику (при значении true сотруднику не будет отправлено письмо на электронную почту с приглашением создать аккаунт). Данный параметр полезен в случае предварительного создания аккаунтов сотрудникам перед их входом через SSO.
    # Return value:
    #   object user.User:   Отредактированный сотрудник
    def user_edit(self, user_id:int,
                    first_name:str=None,
                    last_name:str=None,
                    email:str=None,
                    nickname:str=None,
                    phone_number:str=None,
                    department:str=None,
                    role:str=None,
                    suspended:bool=None,
                    list_tags:List[str]=None,
                    custom_properties:List[CustomProperty]=None,
                    skip_email_notify:bool=None) -> User:
        args = locals()
        url = f'/users/{user_id}'
        json = {
            "user": {
            },
        }
        for arg in list(args)[2:12]:
            if args[arg] is not None:
                json["user"][arg] = Json.loads(Json.dumps(args[arg],
                                                        default=lambda x: getattr(x, '__dict__', str(x)),
                                                        sort_keys=False,
                                                        indent=4))
        if skip_email_notify is not None:
            json["skip_email_notify"] = skip_email_notify
        
        user_json = pachcarequests.send_put_request(self.API_URL + url, self._headers, json=json)

        if not user_json["data"]:
            return {}
        return User(user_json["data"])

    # user_get_info:
    # Arguments:   
    #   user_id:    Идентификатор пользователя
    # Return value:
    #   object user.User: Пользователь, соответствующий предоставленному идентификатору
    def user_get_info(self, user_id) -> User:
        url = f'/users/{user_id}'
        user_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
        if not user_json["data"]:
            return {}
        return User(user_json["data"])
    
    # users_get_all:
    # Arguments:   
    #   filters:    Поисковая фраза для фильтрации результатов (поиск идет по полям first_name (имя), last_name (фамилия), email (электронная почта), phone_number (телефон) и nickname (никнейм))
    # Return value:
    #   list of user.User: Массив списка сотрудников
    def users_get_all(self, filters="") -> List[User]:
        page = 1
        users = []
        if filters:
            query = f'&query={filters}'
        else:
            query = ""

        while True:
            url = f'/users?per=50&page={page}{query}'
            users_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
            
            if not users_json["data"]:
                break
            
            for json in users_json["data"]:
                user = User(json)
                users.append(user)

            page += 1
        
        return users

    # users_get_by_tag:
    # Arguments:   
    #   tag_id:     Идентификатор тега
    # Return value:
    #   list of user.User: Массив списка сотрудников тега
    def users_get_by_tag(self, tag_id:int) -> List[User]:
        page = 1
        users = []

        while True:
            url = f'/group_tags/{tag_id}/users?per=50&page={page}'
            users_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
            
            if not users_json["data"]:
                break
            
            for json in users_json["data"]:
                user = User(json)
                users.append(user)

            page += 1
        
        return users

    # tags_get_all:
    # Arguments:   
    #   None
    # Return value:
    #   list of tag.Tag: Массив списка тегов
    def tags_get_all(self) -> List[Tag]:
        page = 1
        tags = []

        while True:
            url = f'/group_tags?per=50&page={page}'
            tags_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
            
            if not tags_json["data"]:
                break
            
            for json in tags_json["data"]:
                tag = Tag(json)
                tags.append(tag)

            page += 1
        
        return tags
    
    # room_edit:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   name	    Название
    #   public		Доступ: закрытый (по умолчанию, false) или открытый (true)   
    # Return value:
    #   object chatroom.ChatRoom: Отредактированная беседа
    def room_edit(self, room_id:int, name:str=None, public:bool=None) -> ChatRoom:
        args = locals()
        url = f'/chats/{room_id}'
        json = {
            "chat": {
            },
        }
        for arg in list(args)[2:4]:
            if args[arg] is not None:
                json["chat"][arg] = Json.loads(Json.dumps(args[arg],
                                                        default=lambda x: getattr(x, '__dict__', str(x)),
                                                        sort_keys=False,
                                                        indent=4))
        
        chat_json = pachcarequests.send_put_request(self.API_URL + url, self._headers, json=json)

        if not chat_json["data"]:
            return {}
        return ChatRoom(chat_json["data"])

    # room_get_chat_history:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   list of message.Message: Массив всех сообщений в беседе
    def room_get_chat_history(self, room_id) -> List[Message]:
        page = 1
        msgs = []
        while True:
            url = f'/messages?chat_id={room_id}&per=50&page={page}'
            messages = pachcarequests.send_get_request(self.API_URL + url, self._headers)

            if not messages["data"]:
                break
            
            for json in messages["data"]:
                msg = Message(json)
                msgs.append(msg)
                    
            page += 1
        return msgs

    # room_get_cached_history:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   list of message.Message: Массив всех сообщений в беседе, хранящихся в кэше бота
    def room_get_cached_history(self, room_id) -> List[Message]:
        messages = []
        for room in self._my_rooms:
            with room.mutex:
                if room.id == room_id:
                    messages = room.messages
                    break
        return messages

    # room_add_users_by_tag:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   tag_ids:    Идентификаторы тегов, которые будут приглашены в беседу
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def room_add_users_by_tag(self, room_id:int, tag_ids:List[int]) -> Json:
        url = f'/chats/{room_id}/group_tags'
        json = {
            "group_tag_ids": tag_ids
        }
        return pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)

    # room_kick_user_by_tag:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   tag_id:     Идентификатор тега, который будет исключен из беседы
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def room_kick_users_by_tag(self, room_id:int, tag_id:int) -> Json:
        url = f'/chats/{room_id}/group_tags/{tag_id}'
        return pachcarequests.send_delete_request(self.API_URL + url, self._headers)

    # room_add_user_by_id:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   user_ids:   Идентификаторы сотрудников, которые будут приглашены в беседу
    #   silent:     Не создавать в чате системное сообщение о добавлении участника
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def room_add_user_by_id(self, room_id:int, user_ids:List[int], silent:bool=False) -> Json:
        url = f'/chats/{room_id}/members'
        json = {
            "member_ids": user_ids,
            "silent": silent
        }
        return pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)

    # room_kick_user_by_id:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   user_id:    Идентификатор сотрудника, который будет исключен из беседы
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def room_kick_user_by_id(self, room_id:int, user_id:int) -> Json:
        url = f'/chats/{room_id}/members/{user_id}'
        return pachcarequests.send_delete_request(self.API_URL + url, self._headers)

    # room_get_info:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   object chatroom.ChatRoom
    def room_get_info(self, room_id) -> ChatRoom:
        url = f'/chats/{room_id}'
        room_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
        if not room_json["data"]:
            return {}
        return ChatRoom(room_json["data"])
    
    # room_create
    # Arguments:
    #   name	        Название
    #   member_ids	    Массив идентификаторов пользователей, которые станут участниками
    #   group_tag_ids	Массив идентификаторов тегов, которые станут участниками
    #   channel		    Тип: беседа (по умолчанию, false) или канал (true)
    #   public		    Доступ: закрытый (по умолчанию, false) или открытый (true)
    # Return value:
    #   object chatroom.ChatRoom: Созданная беседа или канал
    def room_create(self, name, member_ids:List[int]=None, group_tag_ids:List[int]=None, channel:bool=False, public:bool=False) -> ChatRoom:
        if member_ids is None:
            member_ids = []
        if group_tag_ids is None:
            group_tag_ids = []
        url = f'/chats'
        json = {
            "chat": {
                "name": name,
                "member_ids": member_ids,
                "group_tag_ids": group_tag_ids,
                "channel": channel,
                "public": public
            }
        }
        response = pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)

        if not response["data"]:
            return {}
        return ChatRoom(response["data"])
        

    # rooms_get_all:
    # Arguments:   
    #   None
    # Return value:
    #   list of chatroom.ChatRoom: Каналы, к которым подключен бот
    def rooms_get_all(self) -> List[ChatRoom]:
        return self._my_rooms

    # room_get_users:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   list of user.User: Пользователи, состоящие в беседе
    def room_get_users(self, room_id) -> List[User]:
        users = []
        for room in self._my_rooms:
            if room.id == room_id:
                for user_id in room.member_ids:
                    url = f'/users/{user_id}'
                    user_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
                    if not user_json["data"]:
                        continue
                    users.append(User(user_json["data"]))
        return users

    # message_edit:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    #   content:    Текст сообщения
    #   files:      Прикрепляемые файлы
    # Return value:
    #   object Json: Созданное сообщение в формате Json
    def message_edit(self, msg_id, content="", files:List[File]=None) -> Json:
        if files is None:
            files = []
        url = f'/messages/{msg_id}'
        json = {
            "message": {
                "content": content,
                "files": []
            }
        }
        for file in files:
            json["message"]["files"].append({
                "key": file.key,
                "name": file.name,
                "file_type": file.file_type,
                "size": file.size
            })
        return pachcarequests.send_put_request(self.API_URL + url, self._headers, json=json)

    # message_get_info:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    # Return value:
    #   object message.Message: Информация о сообщении
    def message_get_info(self, msg_id) -> Message:
        url = f'/messages/{msg_id}'
        msg_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
        if not msg_json["data"]:
            return {}
        return Message(msg_json["data"])

    # message_get_reactions:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    # Return value:
    #   list of reaction.Reaction: Массив списка реакций
    def message_get_reactions(self, msg_id) -> List[Reaction]:
        url = f'/messages/{msg_id}/reactions'
        reactions = []
        reactions_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
        if not reactions_json["data"]:
            return reactions
        for reaction_json in reactions_json["data"]:
            reactions.append(Reaction(reaction_json))
        return reactions

    # message_delete_reaction:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    #   emoji:      Emoji символ реакции
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def message_delete_reaction(self, msg_id, emoji) -> Json:
        url = f'/messages/{msg_id}/reactions'
        json = {
            "code": emoji
        }
        return pachcarequests.send_delete_request(self.API_URL + url, self._headers, json=json)

    # message_add_reaction:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    #   emoji:      Emoji символ реакции
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def message_add_reaction(self, msg_id, emoji) -> Json:
        url = f'/messages/{msg_id}/reactions'
        json = {
            'code': emoji,
        }
        return pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)
    
    # message_create_thread:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    # Return value:
    #   object Json: Созданный тред в формате Json
    def message_create_thread(self, msg_id) -> Json:
        url = f'/messages/{msg_id}/thread'
        return pachcarequests.send_post_request(self.API_URL + url, self._headers)["data"]

    # message_reply_in_thread:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    #   content:    Текст сообщения
    #   files:      Прикрепляемые файлы
    # Return value:
    #   object Json: Созданное сообщение в формате Json
    def message_reply_in_thread(self, msg_id, content="", files:List[File]=None) -> Json:
        if files is None:
            files = []
        thread = self.message_create_thread(msg_id)
        url = '/messages'
        json = {
            "message": {
            "entity_type": "thread",
            "entity_id": thread["id"],
            "content": content,
            "files": []
            }
        }
        for file in files:
            json["message"]["files"].append({
                "key": file.key,
                "name": file.name,
                "file_type": file.file_type,
                "size": file.size
            })
        return pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)

    # message_send_in_room:
    # Arguments:
    #   room_id:    Идентификатор беседы или канала
    #   content:    Текст сообщения
    #   files:      Прикрепляемые файлы
    # Return value:
    #   object Json: Созданное сообщение в формате Json
    def message_send_in_room(self, room_id, content="", files:List[File]=None) -> Json:
        if files is None:
            files = []
        url = '/messages'
        json = {
            "message": {
            "entity_type": "discussion",
            "entity_id": room_id,
            "content": content,
            "files": []
            }
        }
        for file in files:
            json["message"]["files"].append({
                "key": file.key,
                "name": file.name,
                "file_type": file.file_type,
                "size": file.size
            })
        return pachcarequests.send_post_request(self.API_URL + url, self._headers, json=json)

    # upload_file:
    # Arguments:
    #   filename: Путь к загружаемому файлу
    # Return value:
    #   object file.File: Загруженный файл
    def upload_file(self, filename) -> File:
        url = "/uploads"
        uploads_json = pachcarequests.send_post_request(self.API_URL + url, self._headers)
        # TODO: Check uploads_json
        direct_url = uploads_json.pop("direct_url")
        try:
            files = { filename: open(filename, 'rb') }
        except Exception as e:
            print(e)
            return {}
        pachcarequests.send_post_request(direct_url, data=uploads_json, files=files)
        
        filepath = uploads_json["key"].replace("${filename}", os.path.basename(filename))
        new_file = File({
            "key": filepath,
            "name": os.path.basename(filename),
            "file_type": "image" if Filetype.is_image(filename) else "file",
            "size": os.path.getsize(filename)
        })
        return new_file

    def on_message(self, func):
        @functools.wraps(func)
        def wrapper(self):
            msg = self.__queue_get()
            if func and msg:
                func(msg)
        self._event_handlers["on_message"] = wrapper
        return wrapper

    def __queue_get(self) -> Message:
        return self._new_msg_queue.get()

    def __update_msg_box(self, room):
        page = 1
        cache_count = 0
        stop = False
        new_msgs = []
        while not stop:
            url = f'/messages?chat_id={room.id}&per=50&page={page}'
            messages = pachcarequests.send_get_request(self.API_URL + url, self._headers)

            if not messages["data"]:
                break
            
            for json in messages["data"]:
                msg = Message(json)
                if msg not in room.messages:
                    new_msgs.append(msg)
                    cache_count += 1
                else:   # message already in cache
                    stop = True
                    break
                if self.cache_size > 0 and cache_count >= self.cache_size:
                    stop = True
                    break
                    
            page += 1
        for new_msg in reversed(new_msgs):
            room.messages.append(new_msg)
        if self.cache_size > 0:
            del room.messages[:len(room.messages) - self.cache_size]
        return new_msgs

    def __room_routine(self, room):
        with room.mutex:
            try:
                updated_room = self.room_get_info(room.id)
            except Exception as e:
                print(e)
                return
            last_msg_time = room.last_message_at
            updated_msg_time = updated_room.last_message_at

            if last_msg_time != updated_msg_time:
                new_msgs = self.__update_msg_box(room)
                for msg in reversed(new_msgs):
                    self._new_msg_queue.put(msg)
            room.update(updated_room)

    def __scan_rooms(self):
        while True:
            for room in self._my_rooms:
                    self.__room_routine(room)
            time.sleep(self.refresh_rate)

    def __chatrooms_init(self):
        url = '/chats'
        rooms_json = pachcarequests.send_get_request(self.API_URL + url, self._headers)
        if not rooms_json["data"]:
            return
        for room in rooms_json["data"]:
            if room["id"] in BLACKLISTED_ROOMS:
                print(f'room {room["name"]} blacklisted')
                continue
            new_room = ChatRoom(room)
            new_room.print_info()
            self._my_rooms.append(new_room)
            self.__update_msg_box(new_room)
            print("=================")
            print(f'room {new_room.name} inited. Message count: {len(new_room.messages)}')
            print("=================")

    def __handle_message(self):
        while True:
            if "on_message" in self._event_handlers:
                self._event_handlers["on_message"](self)
            else:
                msg = self.__queue_get()
                if msg:
                    print(f'msg not handled: user[{msg.user_id}]: {msg.content}')

    def __task_init_sys(self):
        self.__task_create_sys(self.__scan_rooms, "__sys_scan_rooms")
        self.__task_create_sys(self.__handle_message, "__sys_handle_message")

    def __task_create_sys(self, task_function, task_name):
        t = TaskHandle()
        t.name = task_name
        t.thread = threading.Thread(target=task_function, daemon=True)
        self._sys_tasks.append(t)
    
    def __start_tasks_sys(self):
        for task in self._sys_tasks:
            print(f'starting task {task.name}')
            task.thread.start()

    # run
    # Arguments:
    #   None
    # Return value:
    #   None
    def run(self) -> None:
        self.__start_tasks_sys()
        try:
            while True:
                # Could do some work here?
                pass
        except KeyboardInterrupt:
            print("Ctrl+C pressed...")
            sys.exit(1)

