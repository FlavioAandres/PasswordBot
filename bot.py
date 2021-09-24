from posix import environ
from re import split
import telebot
import os
import time

from src import PasswordRepository;
import flask 
API_TOKEN=os.environ.get('BOT_TOKEN')
WEBHOOK_HOST = f"passwordpecuebot.herokuapp.com"
WEBHOOK_PORT = 443  # 443, 80, 88 or 8443 (port need to be 'open')
WEBHOOK_LISTEN = '0.0.0.0'  # In some VPS you may need to put here the IP addr
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}";
WEBHOOK_URL_PATH = f"/{API_TOKEN}/"

bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__); 
chats = {}

# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return {"msg": "Welcome to finances bot API. Find it on Telegram as: @PasswordPecueBot. All opensource contribution is great. "}

@app.route(WEBHOOK_URL_PATH, methods=['POST'])
def webhook():
    if flask.request.headers.get('content-type') == 'application/json':
        json_string = flask.request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return {"msg": "received."}
    else:
        flask.abort(403)

@bot.message_handler(commands=['start', 'help']) 
def _start(message): 
    msg = """
    👋🏻 Hello! Wellcome to Password bot. 
    Use the followings commands: 
    /register 
    /get 
    """;
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['get']) 
def get_password(message): 
    passwordName = ""
    try:
        passwordName = split(' ', message.text)[1];
    except Exception:
        bot.send_message(message.chat.id, "😞 Try again by sending /get <password_name>.")
    
    if(passwordName):
        password = PasswordRepository.get_password(
            name= passwordName, 
            phone=message.from_user.id
        ); 
        msg = f"{password}" if(password) else \
              f"👉🏻 We couldn't find your password for: {passwordName}"; 
        bot.send_message(message.chat.id, msg) 

@bot.message_handler(commands=['getAll'])
def get_all_passwords(message): 
    phone_id = message.from_user.id
    all_passwords = PasswordRepository.get_password(
        phone=phone_id
    ); 
    if(all_passwords): 
        parsed_values = "Your saved passwords: "
        parsed_values += "\n👉🏻".join([str(password) for password in all_passwords])
        bot.send_message(message.chat.id, parsed_values) 





@bot.message_handler(commands=['register']) 
def _register_init(message): 
    msg = """
    Sure, I can surely save your password, please give me the name for the new one: 
    """
    bot.reply_to(message, msg)
    bot.register_next_step_handler(message, _register_get_name); 

def _register_get_name(message):
    password_name = message.text;
    phone_id = message.from_user.id;
    chat_id = message.chat.id
    chats[chat_id] = (password_name, phone_id);
    bot.reply_to(message, "Nice, now give me your password value: ")
    bot.register_next_step_handler(message, _register_get_password_value); 

def _register_get_password_value(message):
    password_value = message.text;
    chat_id = message.chat.id
    password_name = chats[chat_id][0];
    phone_id = chats[chat_id][1];
    PasswordRepository.store_password(
        name=password_name,
        phone=phone_id,
        password=password_value
    );
    bot.send_message(message.chat.id, "Saved successfully")


def start(environment): 
    if(environment == 'test' or environment=="prod"): 
        bot.remove_webhook()
        time.sleep(0.1)
        url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
        # Set webhook
        print(url)
        bot.set_webhook(url=url)
        # Start flask server
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)

    else:
        bot.polling(); 
