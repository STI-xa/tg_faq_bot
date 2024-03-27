import logging
import os

from dotenv import load_dotenv
from telegram import Bot, ReplyKeyboardMarkup, TelegramError
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater
from sqlalchemy import select, or_

from model.db import Question, session

load_dotenv()

secret_token = os.getenv('TOKEN')
operator_chat_id = os.getenv('CHAT_ID')
bot = Bot(secret_token)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)

logger = logging.getLogger(__name__)


def start(update, context):
    """
    При старте бота отправляет сообщение в чат с заданным текстом,
    отобразив пользовательскую клавиатуру с опциями "Готовые вопросы" и "Отправить свой вопрос".
    """
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
    """
    Отправляет сообщение для команды /help.
    """
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Я могу помочь тебе найти ответ на вопрос. "
        "Просто напиши мне свой вопрос.")


def faq(update, context):
    questions = session.execute(select(Question.question)).fetchall()
    session.close()

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
        print(f"При отправке сообщения произошла ошибка: {e}")


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

        result = session.query(Question.answer).filter(Question.question == question).first()

        if not result:
            keywords = question.lower().split()
            query = session.query(Question.answer).filter(
                or_(*[Question.question.ilike(f'%{keyword}%') for keyword in keywords])
            ).first()
            result = query

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
