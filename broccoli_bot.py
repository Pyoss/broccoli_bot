# -*- coding: utf-8 -*-

import telebot
import bot_methods
import test
import spreadsheet_sync
import client_notification
import datetime
import selenium_main
import pickle
import flask_test

admins_id = [197216910, 248343219]

bot = bot_methods.bot

types = telebot.types


def process_order(datadict):
    order = test.Order(test.HookData(datadict))
    message = order.construct_message()
    order_data = test.BucketForShops(message)
    for admin_id in admins_id:
        try:
            bot_methods.send_message(admin_id, message, reply_markup=order.form_keyboard(), parse_mode=None)
        except Exception as e:
            print(e)

    try:
        now = datetime.datetime.now().hour
        if 6 > now or now > 19:
            way, phone, text, name = order_data.get_notice()
            print(way, phone, text, name)
            if way == 'Telegram':
                print(way)
                cn = client_notification.Client_Notice('Здравствуйте, {}!'
                                                       '\nСпасибо за Ваш заказ! ✨ '
                                                       '\nМы работаем ежедневно с 10 до 21, поэтому сейчас наш менеджер не на связи. Мы напишем Вам завтра ☀️ Доброй ночи! 🌌'.format(
                    order.client_name), phone, name)
                bot.queued_processes.append(cn.pulled_notice)
    except Exception as e:
        print(e)


@bot.message_handler(commands=['get_chat_id'])
def start(message):
    try:
        bot_methods.send_message(message.chat.id, str(message.chat.id))
    except Exception as e:
        pass


@bot.message_handler(commands=['pickle'])
def start(message):
    with open('stoplist.pkl', 'wb') as f:
        pickle.dump([], f)


@bot.message_handler(commands=['clear_stoplist'])
def start(message):
    selenium_main.clear_stoplist()


@bot.message_handler(commands=['get_stoplist'])
def start(message):
    with open('stoplist.pkl', 'rb') as f:
        stoplist_for_pickle = pickle.load(f)
    for item in stoplist_for_pickle:
        bot_methods.send_message(197216910, item)


@bot.message_handler(commands=['stoplist'])
def start(message):
    try:
        if len(message.text.split()) > 1:
            shop_name = message.text.split(' ', 1)[1]
            stoplist = test.StopList(spreadsheet_sync.chat_dict[shop_name], admin_mode=True)
        else:
            stoplist = test.StopList(message.chat.id)
        test.redacting_stoplists[message.chat.id] = stoplist
        stoplist.send_stop_list_page(0)
    except Exception as e:
        print(repr(e))


@bot.message_handler(commands=['update_shoplist'])
def start(message):
    try:
        spreadsheet_sync.goods_dict = spreadsheet_sync.get_shops()
        bot_methods.send_message(message.chat.id, 'Список товаров обновлен.')
    except Exception as e:
        bot_methods.send_message(message.chat.id, 'Ошибка:{}'.format(repr(e)))


@bot.message_handler(commands=['test'])
def start(message):
    order = test.Order(test.HookData(test.new_dict))
    message = order.construct_message()
    order_data = test.BucketForShops(message)

    try:
        now = datetime.datetime.now().hour
        print(now)
        if 6 > now or now > 18:
            way, phone, text, name = order_data.get_notice()
            print(way, phone, text, name)
            if way == 'Telegram':
                cn = client_notification.Client_Notice('Здравствуйте, {}! 🌱 '
                                                       '\nСпасибо за Ваш заказ! ✨ '
                                                       '\nМы работаем ежедневно с 9 до 21, поэтому сейчас наш менеджер не на связи. Мы напишем Вам завтра ☀️ Доброй ночи! 🌌'.format(
                    order.client_name), phone, name)
                bot.queued_processes.append(cn.pulled_notice)
    except Exception as e:
        print(e)


@bot.callback_query_handler(func=lambda call: call)
def action(call):
    print(call.data)
    try:
        if call.data[0] == '-':
            pass
        elif call.data.split('_')[0] == 'stoplist':
            if call.message.chat.id not in test.redacting_stoplists:
                bot_methods.answer_callback_query(call, 'Ошибка!', alert=False)
                bot_methods.delete_message(call.message.chat.id, call.message.message_id)
            else:
                test.redacting_stoplists[call.message.chat.id].process_callback(call)
        else:
            message_text = call.message.text
            order_data = test.BucketForShops(message_text)
            if 'send-to-store' in call.data or call.data == 'sent' or call.data == 'cancel':
                reply_data = order_data.reply_to_store(call)
                if reply_data is None:
                    bot_methods.answer_callback_query(call, 'Сообщения уже высланы')
                elif not reply_data[0]:
                    bot_methods.edit_message(call.message.chat.id, call.message.message_id,
                                             message_text=reply_data[1], reply_markup=reply_data[2])
                else:
                    bucket_for_shops = reply_data[1]
                    results = []
                    for key in bucket_for_shops.goods_dict.keys():
                        if key and key in spreadsheet_sync.chat_dict:
                            message = bucket_for_shops.form_message(key, call)
                            chat_id = spreadsheet_sync.chat_dict[key]
                            if chat_id is not None:
                                try:
                                    bot_methods.send_message(chat_id, message)
                                    results.append(key)
                                except Exception as e:
                                    bot_methods.send_message(197216910, repr(e))
                    bot_methods.answer_callback_query(call, text='Успешно отослано в {}'.format(', '.join(results)) if results else 'Доступных чатов нет.')
                    bot_methods.edit_message(call.message.chat.id, call.message.message_id,
                                             message_text=reply_data[2], reply_markup=reply_data[3])

            elif call.data == 'client_notice':
                way, phone, text, name = order_data.get_notice()
                print(way, text, name, phone)
                if way == 'Telegram':
                    sent = client_notification.notice_client(text, phone, name)
                    text = 'Клиент оповещен' if sent else 'Клиент не найден'
                    if sent:
                        bot_methods.answer_callback_query(call, text, alert=False)
                    else:
                        bot_methods.answer_callback_query(call, text, alert=True)
                else:
                    text = 'Клиент не найден'
                    bot_methods.answer_callback_query(call, 'Оповещения поддерживаются только в телеграмме.', alert=True)
                bot_methods.edit_message(call.message.chat.id, call.message.message_id,
                                         message_text=call.message.text + '\n' + text, reply_markup=order_data.form_keyboard(client_sent=True))
    except Exception as e:
        bot_methods.send_message(197216910, repr(e))


if __name__ == '__main__':
    bot.skip_pending = True
    bot.delete_webhook()
    bot.polling(none_stop=True)
