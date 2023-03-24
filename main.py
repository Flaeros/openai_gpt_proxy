import os
from collections import defaultdict
import telebot
from dotenv import load_dotenv
from my_openai import *
import logging

logging.getLogger(__name__)
logging.basicConfig(filename='log.log',
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.WARNING)

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, 'tokens.env'))

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_TOKEN = os.getenv("CHAT_GPT_API_KEY")
BLOCK_LIST = os.getenv("BLOCK_LIST")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = AI_TOKEN

conversations = defaultdict(list)

logging.warning(f'Starting application')

def blocked(message):
    if str(message.from_user.id) in BLOCK_LIST:
        logging.warning(f'Blocked user access {message.from_user.first_name} {message.from_user.id}')
        bot.reply_to(message, text='Вы в черном списке')
        return True

    return False


@bot.message_handler(commands=['bot'])
def command_message(message):
    logging.warning(f'Chat message from {message.from_user.first_name} {message.from_user.id} ')
    if blocked(message):
        return

    respond(message)


@bot.message_handler(commands=['help'])
def command_message(message):
    logging.warning(f'Help message from {message.from_user.first_name} {message.from_user.id} ')
    if blocked(message):
        return

    bot.send_message(message.chat.id, text='/bot или реплай задать вопрос. /clear очистить контекст')


@bot.message_handler(commands=['clean', 'clear'])
def command_message(message):
    logging.warning(f'Cleaning message from {message.from_user.first_name} {message.from_user.id}')
    if blocked(message):
        return

    key = f'{message.chat.type}|{message.chat.id}'
    del conversations[key]
    bot.send_message(message.chat.id, text='Контекст очищен')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    logging.warning(f'Private message from {message.from_user.first_name} {message.from_user.id}')
    if blocked(message):
        return

    respond(message)


def combine_prompts(id, type, text, role):
    key = f'{type}|{id}'
    conversations[key].append({'role': f'{role}', 'content': f'{text}'})
    return conversations[key]


def respond(message):
    prompts = combine_prompts(message.chat.id, message.chat.type, message.text, 'user')

    response = make_request(prompts, AI_TOKEN)
    if response == MAX_LENGTH_ERR_MSG:
        key = f'{message.chat.type}|{message.chat.id}'
        del conversations[key]
        bot.reply_to(message, text='Ошибка, вероятно превышена длина контекста. Диалог завершен, можете начать новый.')
    else:
        combine_prompts(message.chat.id, message.chat.type, response, 'assistant')
        bot.reply_to(message, text=response)


if __name__ == "__main__":
    target = bot.infinity_polling()
