# pachcabot
Bot class for pachca messenger API

Example main.py:
```
import pachcabot

AUTH_TOKEN = YOUR_TOKEN_GOES_HERE
TEST_CHAT = GROUP_ENTITY_ID

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
        if not msg:
            continue
        if msg.user_id == target_user_id and target_user_id != 0 and msg.chat_id == target_chat_id:
            say_happy_birthday(msg)
            print(f'New message from {target_user_lastname}: {msg.content}')
            

bot = pachcabot.PachcaBot(AUTH_TOKEN)

bot.task_create(handle_new_message, "handle_new_message")

bot.run()
```
