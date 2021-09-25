import os; 

WELCOME_EXTRA_MESSAGE = '' if os.environ.get('STAGE') != "dev" else "🚨⚠️ WARNING: Maintance-mode Bot running. You may act with precaation..\n"
def initStartCommand(bot): 
    @bot.message_handler(commands=['start', 'help']) 
    def _start(message): 
        msg = WELCOME_EXTRA_MESSAGE; 
        msg += """
        👋🏻 Hello! Wellcome to Password bot. 
        Use the followings commands: 
        
        💾 /register <password_name>

        🔍 /get 
        🔍 /getAll 
        
        ❌ /delete <exact_password_name>
        """
        bot.send_message(message.chat.id, msg)
