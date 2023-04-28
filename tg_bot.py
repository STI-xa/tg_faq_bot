import logging
import sqlite3
import os

from telegram import Bot, ReplyKeyboardMarkup, TelegramError
from dotenv import load_dotenv
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

load_dotenv()

secret_token = os.getenv('TOKEN')
operator_chat_id = os.getenv('CHAT_ID')
bot = Bot(secret_token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update, context):
    keyboard = [["Готовые вопросы"], ["Отправить свой вопрос"]]

    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True
    )

    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я бот-ассистент. "
        "Я могу помочь тебе найти ответ на вопрос. "
        "Выбери 'Готовые вопросы' или напиши мне свой вопрос.",
        reply_markup=reply_markup
    )


def help(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Я могу помочь тебе найти ответ на вопрос. "
        "Просто напиши мне свой вопрос.")


def faq(update, context):
    conn = sqlite3.connect('faq.db')
    cursor = conn.cursor()
    cursor.execute("SELECT question FROM faq")
    questions = [row[0] for row in cursor.fetchall()]
    conn.close()

    keyboard = [[question] for question in questions]

    reply_markup = ReplyKeyboardMarkup(
        keyboard, one_time_keyboard=True
    )

    try:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Выберите вопрос:",
            reply_markup=reply_markup
        )
    except TelegramError as e:
        print(f"An error occurred while sending a message: {e}")


def echo(update, context):
    message_text = update.message.text

    if message_text == "Готовые вопросы":
        faq(update, context)
    elif message_text == "Напиши свой вопрос":
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="Введите ваш вопрос:"
        )
    else:
        question = message_text

        conn = sqlite3.connect('faq.db')
        cursor = conn.cursor()
        cursor.execute("SELECT answer FROM faq WHERE question=?", (question,))
        result = cursor.fetchone()
        conn.close()

        if not result:
            conn = sqlite3.connect('faq.db')
            cursor = conn.cursor()
            keywords = question.lower().split()
            query = "SELECT answer FROM faq WHERE "
            for keyword in keywords:
                query += f"LOWER(question) LIKE '%{keyword}%' OR "
            query = query[:-4]
            cursor.execute(query)
            result = cursor.fetchone()
            conn.close()

        if result:
            context.bot.send_message(
                chat_id=update.effective_chat.id, text=result[0]
            )
        else:
            context.bot.send_message(
                chat_id=update.effective_chat.id,
                text="Я не знаю ответа на этот вопрос. "
                "Я переадресую его специалисту и он свяжется "
                "с вами в ближайшее время.")
            context.bot.forward_message(
                chat_id=operator_chat_id,
                from_chat_id=update.effective_chat.id,
                message_id=update.message.message_id
            )


if __name__ == '__main__':

    updater = Updater(token=secret_token, use_context=True)

    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    faq_handler = CommandHandler('faq', faq)

    echo_handler = MessageHandler(Filters.text, echo)

    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(faq_handler)
    updater.dispatcher.add_handler(echo_handler)

    updater.start_polling()
    updater.idle()
