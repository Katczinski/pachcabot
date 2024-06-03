import threading 
import time
import sys
import os
import queue
import datetime
import filetype as Filetype
from typing import List
import json as Json

import pachcarequests
from chatroom import ChatRoom
from message import Message
from user import User
from file import File
from task import Task
from reaction import Reaction
from tag import Tag

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
    AUTH_TOKEN = None
    API_URL = "https://api.pachca.com/api/shared/v1"
    my_rooms:List[ChatRoom] = []
    new_msg_queue:List[Message] = None
    headers:object = {}
    cache_size:int = 0
    user_tasks:List[TaskHandle] = []
    _sys_tasks:List[TaskHandle] = []
    uploads = {} # unused

    def __init__(self, auth_token, cache_size=0):
        self.AUTH_TOKEN = auth_token
        self.new_msg_queue = queue.Queue()
        self.uploads = dict()
        self.cache_size = cache_size
        self.headers = {
            'Authorization': f'Bearer {self.AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

    # create_new_task:
    # Arguments:   
    #   kind:           Тип. call (позвонить контакту), meeting (встреча), reminder (напоминание), event (событие), email (написать письмо)
    #   content:        Описание.
    #   due_at:         Срок выполнения задачи. timezone aware!! e.g. datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
    #   priority:       Приоритет. 1 (по умолчанию), 2 (важно) или 3 (очень важно)
    #   performer_ids:  Массив идентификаторов пользователей, привязываемых к задаче как «ответственные»
    # Return value:
    #   object task.Task 
    def create_new_task(self, kind, content, due_at:datetime.datetime, priority, performer_ids:List[int]) -> Task:
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
        response = pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)
        if not response["data"]:
            return {}
        return Task(response["data"])
    
    # get_users_by_tag:
    # Arguments:   
    #   tag_id:     Идентификатор тега
    # Return value:
    #   list of user.User: Массив списка сотрудников тега
    def get_users_by_tag(self, tag_id:int) -> List[User]:
        page = 1
        users = []

        while True:
            url = f'/group_tags/{tag_id}/users?per=50&page={page}'
            users_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
            
            if not users_json["data"]:
                break
            
            for json in users_json["data"]:
                user = User(json)
                users.append(user)

            page += 1
        
        return users

    # get_tags:
    # Arguments:   
    #   None
    # Return value:
    #   list of tag.Tag: Массив списка тегов
    def get_tags(self) -> List[Tag]:
        page = 1
        tags = []

        while True:
            url = f'/group_tags?per=50&page={page}'
            tags_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
            
            if not tags_json["data"]:
                break
            
            for json in tags_json["data"]:
                tag = Tag(json)
                tags.append(tag)

            page += 1
        
        return tags

    # add_tags_to_room:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   tag_ids:    Идентификаторы тегов, которые будут приглашены в беседу
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def add_tags_to_room(self, room_id:int, tag_ids:List[int]) -> Json:
        url = f'/chats/{room_id}/group_tags'
        json = {
            "group_tag_ids": tag_ids
        }
        return pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)

    # kick_tags_from_room:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   tag_id:     Идентификатор тега, который будет исключен из беседы
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def kick_tags_from_room(self, room_id:int, tag_id:int) -> Json:
        url = f'/chats/{room_id}/group_tags/{tag_id}'
        return pachcarequests.send_delete_request(self.API_URL + url, self.headers)

    # add_users_to_room:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   user_ids:   Идентификаторы сотрудников, которые будут приглашены в беседу
    #   silent:     Не создавать в чате системное сообщение о добавлении участника
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def add_users_to_room(self, room_id:int, user_ids:List[int], silent:bool=False) -> Json:
        url = f'/chats/{room_id}/members'
        json = {
            "member_ids": user_ids,
            "silent": silent
        }
        return pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)

    # kick_user_from_room:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    #   user_id:    Идентификатор сотрудника, который будет исключен из беседы
    # Return value:
    #   object Json: При безошибочном выполнении запроса тело ответа отсутствует
    def kick_user_from_room(self, room_id:int, user_id:int) -> Json:
        url = f'/chats/{room_id}/members/{user_id}'
        return pachcarequests.send_delete_request(self.API_URL + url, self.headers)

    # get_room_info:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   object chatroom.ChatRoom
    def get_room_info(self, room_id) -> ChatRoom:
        url = f'/chats/{room_id}'
        room_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        if not room_json["data"]:
            return {}
        return ChatRoom(room_json["data"])
    
    # create_new_room
    # Arguments:
    #   name	        Название
    #   member_ids	    Массив идентификаторов пользователей, которые станут участниками
    #   group_tag_ids	Массив идентификаторов тегов, которые станут участниками
    #   channel		    Тип: беседа (по умолчанию, false) или канал (true)
    #   public		    Доступ: закрытый (по умолчанию, false) или открытый (true)
    # Return value:
    #   object chatroom.ChatRoom: Созданная беседа или канал
    def create_new_room(self, name, member_ids:List[int]=[], group_tag_ids:List[int]=[], channel:bool=False, public:bool=False) -> ChatRoom:
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
        response = pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)

        if not response["data"]:
            return {}
        return ChatRoom(response["data"])
        

    # get_rooms:
    # Arguments:   
    #   None
    # Return value:
    #   list of chatroom.ChatRoom: Каналы, к которым подключен бот
    def get_rooms(self) -> List[ChatRoom]:
        return self.my_rooms

    # get_room_users:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   list of user.User: Пользователи, состоящие в беседе
    def get_room_users(self, room_id) -> List[User]:
        users = []
        for room in self.my_rooms:
            if room.id == room_id:
                for user_id in room.member_ids:
                    url = f'/users/{user_id}'
                    user_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
                    if not user_json["data"]:
                        continue
                    users.append(User(user_json["data"]))
        return users

    # get_user_info:
    # Arguments:   
    #   user_id:    Идентификатор пользователя
    # Return value:
    #   object user.User: Пользователь, соответствующий предоставленному идентификатору
    def get_user_info(self, user_id) -> User:
        url = f'/users/{user_id}'
        user_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        if not user_json["data"]:
            return {}
        return User(user_json["data"])
    
    # get_all_users:
    # Arguments:   
    #   filters:    Поисковая фраза для фильтрации результатов (поиск идет по полям first_name (имя), last_name (фамилия), email (электронная почта), phone_number (телефон) и nickname (никнейм))
    # Return value:
    #   list of user.User: Массив списка сотрудников
    def get_all_users(self, filters="") -> List[User]:
        page = 1
        users = []
        if filters:
            query = f'&query={filters}'
        else:
            query = ""

        while True:
            url = f'/users?per=50&page={page}{query}'
            users_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
            
            if not users_json["data"]:
                break
            
            for json in users_json["data"]:
                user = User(json)
                users.append(user)

            page += 1
        
        return users

    # get_entire_chat_history:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   list of message.Message: Массив всех сообщений в беседе
    def get_entire_chat_history(self, room_id) -> List[Message]:
        page = 1
        msgs = []
        while True:
            url = f'/messages?chat_id={room_id}&per=50&page={page}'
            messages = pachcarequests.send_get_request(self.API_URL + url, self.headers)

            if not messages["data"]:
                break
            
            for json in messages["data"]:
                msg = Message(json)
                msgs.append(msg)
                    
            page += 1
        return msgs

    # get_cached_chat_history:
    # Arguments:   
    #   room_id:    Идентификатор беседы или канала
    # Return value:
    #   list of message.Message: Массив всех сообщений в беседе, хранящихся в кэше бота
    def get_cached_chat_history(self, room_id) -> List[Message]:
        for room in self.my_rooms:
            if room.id == room_id:
                return room.messages
        return []

    # message_edit:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    #   content:    Текст сообщения
    #   files:      Прикрепляемые файлы
    # Return value:
    #   object Json: Созданное сообщение в формате Json
    def message_edit(self, msg_id, content="", files:List[File]=[]) -> Json:
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
        return pachcarequests.send_put_request(self.API_URL + url, self.headers, json=json)
        
    # message_get_reactions:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    # Return value:
    #   list of reaction.Reaction: Массив списка реакций
    def message_get_reactions(self, msg_id) -> List[Reaction]:
        url = f'/messages/{msg_id}/reactions'
        reactions = []
        reactions_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        if not reactions_json["data"]:
            return reactions
        for reaction_json in reactions_json["data"]:
            reactions.append(Reaction(reaction_json))
        return reactions

    # message_get_info:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    # Return value:
    #   object message.Message: Информация о сообщении
    def message_get_info(self, msg_id) -> Message:
        url = f'/messages/{msg_id}'
        msg_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        if not msg_json["data"]:
            return {}
        return Message(msg_json["data"])
        
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
        return pachcarequests.send_delete_request(self.API_URL + url, self.headers, json=json)

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
        return pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)
    
    # message_create_thread:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    # Return value:
    #   object Json: Созданный тред в формате Json
    def message_create_thread(self, msg_id) -> Json:
        url = f'/messages/{msg_id}/thread'
        return pachcarequests.send_post_request(self.API_URL + url, self.headers)["data"]

    # message_reply_in_thread:
    # Arguments:
    #   msg_id:     Идентификатор сообщения
    #   content:    Текст сообщения
    #   files:      Прикрепляемые файлы
    # Return value:
    #   object Json: Созданное сообщение в формате Json
    def message_reply_in_thread(self, msg_id, content="", files:List[File]=[]) -> Json:
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
        return pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)

    # message_send_in_room:
    # Arguments:
    #   room_id:    Идентификатор беседы или канала
    #   content:    Текст сообщения
    #   files:      Прикрепляемые файлы
    # Return value:
    #   object Json: Созданное сообщение в формате Json
    def message_send_in_room(self, room_id, content="", files:List[File]=[]) -> Json:
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
        return pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)
    
    # queue_get:
    # Arguments:
    #   None
    # Return value:
    #   object message.Message: Первое сообщение в очереди (FIFO) новых сообщений
    def queue_get(self) -> Message:
        return self.new_msg_queue.get()

    # upload_file:
    # Arguments:
    #   filename: Путь к загружаемому файлу
    # Return value:
    #   object file.File: Загруженный файл
    def upload_file(self, filename) -> File:
        url = "/uploads"
        uploads_json = pachcarequests.send_post_request(self.API_URL + url, self.headers)
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

    # task_create:
    # Arguments:
    #   task_function:  Функция, исполняющая рутину создаваемой задачи
    #   task_name:      Именной идентификатор функции
    # Return value:
    #   object TaskHandle: Дескриптор созданной задачи
    def user_task_create(self, task_function, task_name) -> TaskHandle:
        t = TaskHandle()
        t.name = task_name
        t.thread = threading.Thread(target=task_function, daemon=True)
        self.user_tasks.append(t)
        return t

    def __update_msg_box(self, room):
        page = 1
        cache_count = 0
        stop = False
        new_msgs = []
        while not stop:
            url = f'/messages?chat_id={room.id}&per=50&page={page}'
            messages = pachcarequests.send_get_request(self.API_URL + url, self.headers)

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
                updated_room = self.get_room_info(room.id)
            except Exception as e:
                print(e)
                return
            last_msg_time = room.last_message_at
            updated_msg_time = updated_room.last_message_at

            if last_msg_time != updated_msg_time:
                new_msgs = self.__update_msg_box(room)
                for msg in reversed(new_msgs):
                    self.new_msg_queue.put(msg)
                room.last_message_at = updated_room.last_message_at

    def __scan_rooms(self):
        while True:
            for room in self.my_rooms:
                    self.__room_routine(room)
            time.sleep(2)

    def __chatrooms_init(self):
        url = '/chats'
        rooms_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        if not rooms_json["data"]:
            return
        for room in rooms_json["data"]:
            if room["id"] in BLACKLISTED_ROOMS:
                print(f'room {room["name"]} blacklisted')
                continue
            new_room = ChatRoom(room)
            new_room.print_info()
            self.my_rooms.append(new_room)
            self.__update_msg_box(new_room)
            print(f'room {new_room.name} inited. Message count: {len(new_room.messages)}')

    def __task_init_sys(self):
        self.__task_create_sys(self.__scan_rooms, "__sys_scan_rooms")

    def __task_create_sys(self, task_function, task_name):
        t = TaskHandle()
        t.name = task_name
        t.thread = threading.Thread(target=task_function, daemon=True)
        self._sys_tasks.append(t)
    
    def __start_tasks_sys(self):
        for task in self._sys_tasks:
            print(f'starting task {task.name}')
            task.thread.start()

    def __start_tasks(self):
        for task in self.user_tasks:
            print(f'starting task {task.name}')
            task.thread.start()
    # run
    # Arguments:
    #   None
    # Return value:
    #   None
    def run(self) -> None:
        self.__chatrooms_init()
        self.__task_init_sys()
        self.__start_tasks_sys()
        self.__start_tasks()
        try:
            while True:
                # Could do some work here
                pass
        except KeyboardInterrupt:
            print("Ctrl+C pressed...")
            sys.exit(1)

