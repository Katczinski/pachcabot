# pachcabot
Bot class for pachca messenger API\
Developed with Python 3.7.9

Implemented methods:\
✅ Загрузка файлов\
✅ Список сотрудников\
✅ Информация о сотруднике\
❌ Текущий статус\
❌ Новый статус\
❌ Удаление статуса\
❌ Список тегов сотрудников\
❌ Список сотрудников тега\
❌ Новая беседа или канал\
❌ Информация о беседе и канале\
✅ Список бесед и каналов\
❌ Добавление пользователей\
❌ Добавление тегов\
✅ Новый тред\
✅ Новое сообщение\
✅ Информация о сообщении\
✅ Список сообщений чата\
❌ Редактирование сообщения\
✅ Добавление реакции\
✅ Удаление реакции\
❌ Список реакций\
❌ Новая задача

Example main.py:
```
import pachcabot

AUTH_TOKEN = YOUR_API_TOKEN_GOES_HERE
TEST_CHAT = GROUP_ENTITY_ID_GOES_HERE   # for the sake of example
BOT_ID = BOT_USER_ID_GOES_HERE          # for the sake of example

def say_happy_birthday(msg):
  bot.message_reply_in_thread(msg.id, "Happy Birthday!!!🎂🎂🎂")
  bot.message_react(msg.id, '🎂')

def handle_new_message():
    target_user_lastname = "Smith"
    target_user_id = 0
    target_chat_id = TEST_CHAT

    users = bot.get_room_users(target_chat_id)

    for user in users:
        if user.last_name == target_user_lastname:
            target_user_id = user.id
            print(target_user_lastname, "found:", target_user_id)

    while True:
        msg = bot.queue_get()
        if not msg or msg.user_id == BOT_ID:
            continue
        if msg.user_id == target_user_id and target_user_id != 0 and msg.chat_id == target_chat_id:
            say_happy_birthday(msg)
            print(f'New message from {target_user_lastname}: {msg.content}')
            

bot = pachcabot.PachcaBot(AUTH_TOKEN)

bot.task_create(handle_new_message, "handle_new_message")

bot.run()
```
