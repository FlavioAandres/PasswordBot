from re import split
from .. import PasswordRepository;

chats = {}


def initRegisterCommands(bot):
    @bot.message_handler(commands=['register']) 
    def _register_init(message): 
        text = split(pattern=" ", string=message.text)
        phone_id = message.from_user.id;
        chat_id = message.chat.id
        name_input = text[1] if len(text) > 1 else None; 

        """
        if password name was given in /register <password_name>
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
            message_response = "👩🏻‍✈️ Sure, I can surely save your password, please give me the name for the new one: "\
                               "<i> cancel with: /stop </i>";
            bot.register_next_step_handler(message, _register_get_name); 
        
        bot.reply_to(message, message_response, parse_mode='HTML')

    def _register_get_name(message):
        password_name = message.text;
        if password_name == "/stop": 
            return bot.send_message(message.chat.id, "👮‍♀️🛑✋ Operation stopped.")
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