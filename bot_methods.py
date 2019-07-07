#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot

bot = telebot.TeleBot('547528483:AAFxVwtPOM6tvk8GLPei1a1v1jvcH4CYgTw', threaded=False)

# Переопределение метода отправки сообщения (защита от ошибок)
def send_message(chat_id, message, reply_markup=None, parse_mode=None):
    print(chat_id)
    return bot.send_message(chat_id, message, reply_markup=reply_markup, parse_mode=parse_mode)


def edit_message(chat_id, message_id, message_text, reply_markup=None, parse_mode=None):
    try:
        return bot.edit_message_text(chat_id=chat_id, message_id=message_id,
                                     text=message_text, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        print(e)


def send_image(image, chat_id, message=None, reply_markup=None):
    return bot.send_photo(chat_id=chat_id, caption=message, photo=image, reply_markup=reply_markup)


def delete_message(chat_id=None, message_id=None, call=None):
    try:
        if call is not None:
            return bot.delete_message(call.message.chat.id, call.message.message_id)
        return bot.delete_message(chat_id, message_id)
    except Exception as e:
        print(e)


def answer_callback_query(call, text, alert=True):
    bot.answer_callback_query(call.id, text=text, show_alert=alert)
