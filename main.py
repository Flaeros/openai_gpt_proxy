import os
from collections import defaultdict
import telebot
from telebot import types
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
dialogs = defaultdict(bool)

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
    if key in conversations:
        del conversations[key]
    if key in dialogs:
        del dialogs[key]

    bot.send_message(message.chat.id, text='Контекст очищен')


@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "start_dialog":
        bot.answer_callback_query(call.id, "Диалог начат")
        start_dialog(call.message)
    elif call.data == "end_dialog":
        bot.answer_callback_query(call.id, "Диалог завершен")
        end_dialog(call.message)


def start_dialog(message):
    logging.warning(f'Starting dialog  {message.from_user.first_name} {message.from_user.id}')
    key = f'{message.chat.type}|{message.chat.id}'
    dialogs[key] = True

    keyboard = get_keyboard(True)
    bot.reply_to(message, text='Диалог начат. Теперь бот будет запоминать сообщения', reply_markup=keyboard)


def end_dialog(message):
    logging.warning(f'Ending dialog  {message.from_user.first_name} {message.from_user.id}')
    key = f'{message.chat.type}|{message.chat.id}'

    if key in conversations:
        del conversations[key]
    if key in dialogs:
        del dialogs[key]

    keyboard = get_keyboard(False)
    bot.reply_to(message, text='Диалог завершен', reply_markup=keyboard)


@bot.message_handler(func=lambda message: True)
def echo_all(message):
    logging.warning(f'Private message from {message.from_user.first_name} {message.from_user.id}')
    if blocked(message):
        return

    respond(message)


def combine_prompts(key, text, role):
    conversations[key].append({'role': f'{role}', 'content': f'{text}'})
    return conversations[key]


def respond(message):
    key = f'{message.chat.type}|{message.chat.id}'

    dialog = dialogs[key]
    keyboard = get_keyboard(dialog)

    if dialog:
        prompts = combine_prompts(key, message.text, 'user')
    else:
        prompts = [{'role': 'user', 'content': message.text}]

    response = make_request(prompts, AI_TOKEN)
    if response == MAX_LENGTH_ERR_MSG:
        if key in conversations:
            del conversations[key]
        if key in dialogs:
            del dialogs[key]
        bot.reply_to(message, text='Ошибка, вероятно превышена длина контекста. Диалог завершен, можете начать новый.')
    else:
        if dialog:
            combine_prompts(key, response, 'assistant')
        bot.reply_to(message, text=response, reply_markup=keyboard)


def get_keyboard(dialog):
    keyboard = types.InlineKeyboardMarkup()
    if dialog:
        button_end_dialog = types.InlineKeyboardButton('Завершить диалог', callback_data='end_dialog')
        keyboard.add(button_end_dialog)
    else:
        button_start_dialog = types.InlineKeyboardButton('Начать диалог', callback_data='start_dialog')
        keyboard.add(button_start_dialog)
    return keyboard


if __name__ == "__main__":
    target = bot.infinity_polling()
