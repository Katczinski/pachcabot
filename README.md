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
import pachcabot
from message import Message

AUTH_TOKEN = YOUR_API_TOKEN_GOES_HERE       # string  # required!
TARGET_CHAT = GROUP_ENTITY_ID_GOES_HERE     # integer # for the sake of example
BOT_ID = BOT_USER_ID_GOES_HERE              # integer # for the sake of example

def say_happy_birthday(msg):
  bot.message_reply_in_thread(msg.id, "Happy Birthday!!!🎂🎂🎂")
  bot.message_add_reaction(msg.id, '🎂')

bot = pachcabot.PachcaBot(AUTH_TOKEN, cache_size=20)

user = bot.users_get_all(filters="Smith")[0]

@bot.on_message
def message_handler(msg:Message):
    if msg.user_id == BOT_ID:
        return
    if msg.user_id == user.id and user.id != 0:
        print(f'New message from {user.last_name}: {msg.content}')   
        say_happy_birthday(msg)       

bot.run()
```
