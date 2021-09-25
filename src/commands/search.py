from .. import PasswordRepository;
from re import split
from telebot import types as TelebotTypes 

def initSearchCommands(bot): 
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
