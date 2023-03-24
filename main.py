import os
from collections import defaultdict
import telebot
from dotenv import load_dotenv
from my_openai import *

BASEDIR = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(BASEDIR, 'tokens.env'))

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AI_TOKEN = os.getenv("CHAT_GPT_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)
openai.api_key = AI_TOKEN

conversations = defaultdict(list)

@bot.message_handler(commands=['bot'])
def command_message(message):
    respond(message)


@bot.message_handler(commands=['help'])
def command_message(message):
    bot.send_message(message.chat.id, text='/bot или реплай задать вопрос. /clear очистить контекст')


@bot.message_handler(commands=['clean', 'clear'])
def command_message(message):
    key = f'{message.chat.type}|{message.chat.id}'
    del conversations[key]
    bot.send_message(message.chat.id, text='Контекст очищен')


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    respond(message)


def combine_prompts(id, type, text, role):
    key = f'{type}|{id}'
    conversations[key].append({'role': f'{role}', 'content': f'{text}'})
    return conversations[key]


def respond(message):
    prompts = combine_prompts(message.chat.id, message.chat.type, message.text, 'user')

    response = make_request(prompts, AI_TOKEN)
    combine_prompts(message.chat.id, message.chat.type, response, 'assistant')
    bot.reply_to(message, text=response)


if __name__ == "__main__":
    target = bot.infinity_polling()
