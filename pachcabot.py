import requests
import json
import threading 
import time
import sys
import os
import queue
import filetype as Filetype
from typing import List

import pachcarequests
from chatroom import ChatRoom
from message import Message
from user import User
from file import File

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
    my_rooms = []
    new_msg_queue = None
    headers = {}
    cache_size = 0
    user_tasks = []
    _sys_tasks = []
    uploads = {}

    def __init__(self, auth_token, cache_size=0):
        self.AUTH_TOKEN = auth_token
        self.new_msg_queue = queue.Queue()
        self.uploads = dict()
        self.cache_size = cache_size
        self.headers = {
            'Authorization': f'Bearer {self.AUTH_TOKEN}',
            'Content-Type': 'application/json'
        }

    def get_room_info(self, room_id):
        url = f'/chats/{room_id}'
        room_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        return ChatRoom(room_json["data"])

    def get_rooms(self):
        return self.my_rooms

    def get_room_users(self, room_id):
        users = []
        for room in self.my_rooms:
            if room.id == room_id:
                for user_id in room.member_ids:
                    url = f'/users/{user_id}'
                    user_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
                    users.append(User(user_json["data"]))
        return users

    def get_user_info(self, user_id):
        url = f'/users/{user_id}'
        user_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        return User(user_json["data"])

    def get_all_users(self, filters=""):
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

    def get_entire_chat_history(self, room_id):
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

    def get_cached_chat_history(self, room_id):
        for room in self.my_rooms:
            if room.id == room_id:
                return room.messages
        return []

    def message_get_info(self, msg_id):
        url = f'/messages/{msg_id}'
        msg_json = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        return Message(msg_json["data"])

    def message_delete_reaction(self, msg_id, emoji):
        url = f'/messages/{msg_id}/reactions'
        json = {
            "code": emoji
        }
        return pachcarequests.send_delete_request(self.API_URL + url, self.headers, json=json)

    def message_react(self, msg_id, emoji):
        url = f'/messages/{msg_id}/reactions'
        json = {
            'code': emoji,
        }
        return pachcarequests.send_post_request(self.API_URL + url, self.headers, json=json)

    def message_create_thread(self, msg_id):
        url = f'/messages/{msg_id}/thread'
        return pachcarequests.send_post_request(self.API_URL + url, self.headers)["data"]

    def message_reply_in_thread(self, msg_id, content="", files:List[File]=[]):
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

    def message_send_in_room(self, room_id, content="", files:List[File]=[]):
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

    def queue_get(self):
        return self.new_msg_queue.get()

    def upload_file(self, filename):
        url = "/uploads"
        uploads = pachcarequests.send_post_request(self.API_URL + url, self.headers)
        direct_url = uploads.pop("direct_url")
        try:
            files = { filename: open(filename, 'rb') }
        except Exception as e:
            print(e)
            return File()
        pachcarequests.send_post_request(direct_url, data=uploads, files=files)
        
        filepath = uploads["key"].replace("${filename}", os.path.basename(filename))
        new_file = File({
            "key": filepath,
            "name": os.path.basename(filename),
            "file_type": "image" if Filetype.is_image(filename) else "file",
            "size": os.path.getsize(filename)
        })
        return new_file

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
        rooms = pachcarequests.send_get_request(self.API_URL + url, self.headers)
        for room in rooms["data"]:
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

    def task_create(self, task_function, task_name):
        t = TaskHandle()
        t.name = task_name
        t.thread = threading.Thread(target=task_function, daemon=True)
        self.user_tasks.append(t)
        return t
    
    def __start_tasks_sys(self):
        for task in self._sys_tasks:
            print(f'starting task {task.name}')
            task.thread.start()

    def __start_tasks(self):
        for task in self.user_tasks:
            print(f'starting task {task.name}')
            task.thread.start()

    def run(self):
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

