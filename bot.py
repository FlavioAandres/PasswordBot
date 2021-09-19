from posix import environ
from re import split
import telebot
import os
bot = telebot.TeleBot(os.environ.get('BOT_TOKEN'))
from src import PasswordRepository;

chats = {}

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
        bot.set_webhook(
            url=f"https://passwordpecuebot.herokuapp.com:{os.environ.get('PORT', 5000)}"
        )
    else:
        bot.polling(); 
