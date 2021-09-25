from telebot import types as TelebotTypes, telebot 
import os;
API_TOKEN=os.environ.get('BOT_TOKEN')

def getBotInstance():
    return telebot.TeleBot(API_TOKEN)