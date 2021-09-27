from dotenv import load_dotenv;
load_dotenv(); 
import bot
import os
import flask 
from telebot import types as TelebotTypes 
import time; 
from src.commands import register, search, start as startCommand; 

API_TOKEN=os.environ.get('BOT_TOKEN'); 
WEBHOOK_HOST = os.environ.get('WEBHOOK_HOST'); 
WEBHOOK_PORT = os.environ.get('WEBHOOK_PORT', 443); 
WEBHOOK_LISTEN = os.environ.get('WEBHOOK_LISTEN', '0.0.0.0'); 
WEBHOOK_URL_BASE = f"https://{WEBHOOK_HOST}:{WEBHOOK_PORT}";
WEBHOOK_URL_PATH = f"/{API_TOKEN}/"; 

app = flask.Flask(__name__); 

# Empty webserver index, return nothing, just http 200
@app.route('/', methods=['GET', 'HEAD'])
def index():
    return {"msg": "Welcome to password-bot API. Find it on Telegram as: @PasswordPecueBot. All opensource contribution is great. "}

def initializeBotRoute(botClient): 
    @app.route(WEBHOOK_URL_PATH, methods=['POST'])
    def webhook():
        if flask.request.headers.get('content-type') == 'application/json':
            json_string = flask.request.get_data().decode('utf-8')
            update = TelebotTypes.Update.de_json(json_string)
            botClient.process_new_updates([update])
            return {"msg": "received."}
        else:
            flask.abort(403)

def start(environment): 
    botClient = bot.getBotInstance(); 
    ## Configure commands
    initializeBotRoute(botClient)
    search.initSearchCommands(botClient); 
    register.initRegisterCommands(botClient);
    startCommand.initStartCommand(botClient); 

    if(environment == 'test' or environment=="prod"): 
        botClient.remove_webhook()
        time.sleep(0.1)
        url = WEBHOOK_URL_BASE + WEBHOOK_URL_PATH
        # Set webhook
        print(url)
        botClient.set_webhook(url=url)
        # Start flask server
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
    else:
        botClient.remove_webhook()
        print('(-.-)::password-bot -> initialized')
        botClient.polling(); 


if __name__ == '__main__': 
    start(os.environ.get('STAGE')); 

