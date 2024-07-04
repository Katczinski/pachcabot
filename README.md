# pachcabot
Bot class for pachca messenger API\
Developed with Python 3.7.9

## The master branch has been abandoned indefinitely due to the current pachca API not providing a comprehensive way to implement an events-driven system without using webhooks.

### Implemented methods:
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

AUTH_TOKEN = YOUR_API_TOKEN_GOES_HERE       # string  # required!
TARGET_CHAT = GROUP_ENTITY_ID_GOES_HERE     # integer # for the sake of example
BOT_ID = BOT_USER_ID_GOES_HERE              # integer # for the sake of example

def say_happy_birthday(msg):
  bot.message_reply_in_thread(msg.id, "Happy Birthday!!!🎂🎂🎂")
  bot.message_add_reaction(msg.id, '🎂')

bot = pachca.Client(AUTH_TOKEN, cache_size=20)

birthday_boy = bot.users_get_all(filters="Smith")[0]

@bot.on_message
def message_handler(msg:Message):
    if msg.user_id == BOT_ID:
        return
    if birthday_boy and msg.user_id == birthday_boy.id:
        print(f'New message from {birthday_boy.last_name} {birthday_boy.first_name}: {msg.content}')   
        say_happy_birthday(msg)       

@bot.on_ready
def say_hello():
    rooms = bot.rooms_get_all()
    for room in rooms:
        bot.message_send_in_room(room.id, "I'm alive!")

bot.run()    
```
