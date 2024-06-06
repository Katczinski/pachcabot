# pachcabot
Bot class for pachca messenger API\
Developed with Python 3.7.9

Implemented methods:\
**Общие методы:**\
✅ Список дополнительных полей\
✅ Загрузка файлов\
**Сотрудники:**\
✅ Новый сотрудник\
✅ Список сотрудников\
✅ Информация о сотруднике\
✅ Редактирование сотрудника\
✅ Удаление сотрудника\
**Статус:**\
❌ Текущий статус\
❌ Новый статус\
❌ Удаление статуса\
**Теги:**\
✅ Список тегов сотрудников\
✅ Список сотрудников тега\
**Беседы и каналы:**\
✅ Новая беседа или канал\
✅ Информация о беседе и канале\
✅ Список бесед и каналов\
✅ Обновление беседы или канала\
**Участники бесед и каналов:**\
✅ Добавление пользователей\
✅ Исключение пользователя\
✅ Добавление тегов\
✅ Исключение тега\
**Комментарии:**\
✅ Новый тред\
**Сообщения:**\
✅ Новое сообщение\
✅ Информация о сообщении\
✅ Список сообщений чата\
✅ Редактирование сообщения\
**Реакции на сообщения:**\
✅ Добавление реакции\
✅ Удаление реакции\
✅ Список реакций\
**Задачи:**\
✅ Новая задача

Example main.py:
```
import pachca
from pachca.types import Message
from pachca.types import Reaction

AUTH_TOKEN = YOUR_API_TOKEN_GOES_HERE       # string  # required!
TARGET_CHAT = GROUP_ENTITY_ID_GOES_HERE     # integer # for the sake of example
BOT_ID = BOT_USER_ID_GOES_HERE              # integer # for the sake of example

HOST = "localhost"
PORT = 5000

def say_happy_birthday(msg):
  bot.message_reply_in_thread(msg.id, "Happy Birthday!!!🎂🎂🎂")
  bot.message_add_reaction(msg.id, '🎂')

bot = pachca.Client(AUTH_TOKEN)

birthday_boy = bot.users_get_all(filters="Smith")[0]

@bot.on_message
def message_handler(msg:Message):
    if msg.user_id == BOT_ID:
        return
    if birthday_boy and msg.user_id == birthday_boy.id:
        print(f'New message from {birthday_boy.last_name} {birthday_boy.first_name}: {msg.content}')   
        say_happy_birthday(msg)       

@bot.on_message_delete
def message_handler(msg:Message):
    user = bot.user_get_info(msg.user_id)
    print(f'{user.first_name} {user.last_name} deleted message {msg.content}')

@bot.on_message_edit
def message_handler(msg:Message):
    user = bot.user_get_info(msg.user_id)
    print(f'{user.first_name} {user.last_name} edited message {msg.content}')

@bot.on_reaction_remove
def message_handler(react:Reaction):
    msg = bot.message_get_info(react.message_id)
    user = bot.user_get_info(react.user_id)
    print(f'Reaction {react.code} removed by {user.first_name} {user.last_name} from the message {msg.content}')

@bot.on_reaction_add
def message_handler(react:Reaction):
    msg = bot.message_get_info(react.message_id)
    user = bot.user_get_info(react.user_id)
    print(f'Reaction {react.code} added by {user.first_name} {user.last_name} to the message {msg.content}')

@bot.on_ready
def say_hello():
    rooms = bot.rooms_get_all()
    for room in rooms:
        bot.message_send_in_room(room.id, "I'm alive!")

bot.run(HOST, PORT)    
```
