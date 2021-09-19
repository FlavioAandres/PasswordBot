from dotenv import load_dotenv;
load_dotenv(); 
import sys
import bot
import os
from src import PasswordRepository as Password;

if __name__ == '__main__': 
    bot.start(os.environ.get('STAGE')); 

