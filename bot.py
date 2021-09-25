from posix import environ
from re import split
from telebot import types as TelebotTypes, telebot 
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
WELCOME_EXTRA_MESSAGE = '' if os.environ.get('STAGE') != "dev" else "🚨WARNING: Maintance-mode Bot running...\n"
bot = telebot.TeleBot(API_TOKEN)
app = flask.Flask(__name__); 
chats = {}

# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return {"msg": "Welcome to password-bot API. Find it on Telegram as: @PasswordPecueBot. All opensource contribution is great. "}

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
    msg = f"""
    {WELCOME_EXTRA_MESSAGE}
    👋🏻 Hello! Wellcome to Password bot. 
    Use the followings commands: 
    /register 
    /get 
    /getAll 
    
    """;
    bot.send_message(message.chat.id, msg)

@bot.message_handler(commands=['get']) 
def get_password(message): 
    passwordName = ""
    try:
        passwordName = split(' ', message.text)[1];
    except Exception:
        bot.send_message(message.chat.id, "😞 Try again by sending /get <password_name>.")
    msg=""
    if(passwordName):
        password = PasswordRepository.get_password(
            name= passwordName, 
            phone=message.from_user.id
        ); 
        if isinstance(password, list):
            markup = TelebotTypes.ReplyKeyboardMarkup()
            options = list(map(lambda pass_name: TelebotTypes.KeyboardButton(pass_name), password))
            markup.row(*options)
            bot.register_next_step_handler(message, _get_password_value); 
            return bot.send_message(message.chat.id, "You've many options to choose, select one:  ", reply_markup=markup)
        else:
            msg = f"{password}" if password else \
                f"👉🏻 We couldn't find your password for: {passwordName}"; 
        
        bot.send_message(message.chat.id, msg) 

def _get_password_value(message):
    text = message.text
    password = PasswordRepository.get_password(
        name=text, 
        phone=message.from_user.id
    ); 
    if password != None: 
        msg=f"{password}"
    else: 
        msg = "🙅🏼‍♀️: Wrong password passed."
    bot.send_message(message.chat.id, msg) 

@bot.message_handler(commands=['getAll'])
def get_all_passwords(message): 
    phone_id = message.from_user.id
    all_passwords = PasswordRepository.get_password(
        phone=phone_id
    ); 
    if(all_passwords): 
        parsed_values = "Your saved passwords: \n👉🏻"
        parsed_values += "\n👉🏻".join([str(password) for password in all_passwords])
        bot.send_message(message.chat.id, parsed_values) 
    else: 
        bot.send_message(message.chat.id, "🧟‍♀️ We couldn't find any password saved.") 




@bot.message_handler(commands=['register']) 
def _register_init(message): 
    text = split(pattern=" ", string=message.text)
    phone_id = message.from_user.id;
    chat_id = message.chat.id
    name_input = text[1] if len(text) > 1 else None; 

    """
    if password was given in /register <password>
    """
    if name_input != None: 
        existsName = PasswordRepository.get_password(phone=phone_id, name=name_input)
        if existsName != None:
            message_response="🙅🏼‍♀️ This password name already exists. Use a new one"
        else: 
            chats[chat_id] = (name_input, phone_id);
            message_response = "✅ Nice, now give me your password value: "
            bot.register_next_step_handler(message, _register_get_password_value); 
    else: 
        message_response = """
        👩🏻‍✈️ Sure, I can surely save your password, please give me the name for the new one: 
        """
        bot.register_next_step_handler(message, _register_get_name); 
    
    bot.reply_to(message, message_response)

def _register_get_name(message):
    password_name = message.text;
    phone_id = message.from_user.id;
    chat_id = message.chat.id
    existsName = PasswordRepository.get_password(phone=phone_id, name=password_name)
    message_response=""
    if existsName != None:
        message_response="🙅🏼‍♀️ This password name already exists. Use a new one."
    else:
        chats[chat_id] = (password_name, phone_id);
        message_response = "✅ Nice, now give me your password value: "
        
    bot.reply_to(message, message_response)
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
        bot.remove_webhook()
        print('(-.-)::password-bot -> initialized')
        bot.polling(); 
