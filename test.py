#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import spreadsheet_sync
import math
import pickle
import bot_methods

redacting_stoplists = {}


class HookData:
    def __init__(self, request_form_dict):
        self.dict = {}
        temp_dicts = {}
        temp_dicts_1 = {}
        for key, value in request_form_dict.items():
            key = key.replace('data', '')
            data_tuple = list(key.split(']['))
            data_tuple = [item.replace(']', '').replace('[', '') for item in data_tuple]

            if len(data_tuple) == 1:
                self.dict[data_tuple[0]] = value[0]
            elif len(data_tuple) == 2:
                destination = data_tuple[0]
                keyword = data_tuple[1]
                self.add_to_dicted(temp_dicts_1, destination, keyword, value[0])
            elif len(data_tuple) == 3:
                destination = data_tuple[0]
                number = data_tuple[1]
                keyword = data_tuple[2]
                if destination in temp_dicts:
                    self.add_to_dicted(temp_dicts[destination], number, keyword, value[0])
                else:
                    temp_dicts[destination] = {number: {keyword: value[0]}}
            elif len(data_tuple) == 4:
                destination = data_tuple[0]
                number = data_tuple[1]
                keyword = data_tuple[2]
                if destination in temp_dicts:
                    self.add_to_dicted_list(temp_dicts[destination], number, keyword, value[0])
                else:
                    temp_dicts[destination] = {number: {keyword: [value[0]]}}

        for k, v in temp_dicts.items():
            for x, y in v.items():
                self.add_to_dict(temp_dicts_1, k, y)

        self.dict = {**self.dict, **temp_dicts_1}

    @staticmethod
    def add_to_dicted(dct, ky, keyword, value):
        if ky in dct:
            dct[ky][keyword] = value
        else:
            dct[ky] = {keyword: value}

    @staticmethod
    def add_to_dicted_list(dct, ky, keyword, value):
        if ky in dct:
            if keyword in dct[ky]:
                dct[ky][keyword].append(value)
            else:
                dct[ky][keyword] = [value]
        else:
            dct[ky] = {keyword: [value]}

    @staticmethod
    def add_to_dict(dct, ky, item):
        if ky in dct:
            dct[ky].append(item)
        else:
            dct[ky] = [item]


class Order:
    def __init__(self, hookdata):
        self.dict = hookdata.dict
        print(self.dict)
        self.switch = False
        self.strings_list = []
        self.working_list = []
        self.client_name = None
        self.weight = 0
        self.form_working_list()

    def construct_message(self):
        message = ''
        if any(70 >= msg_strng.order > 60 for msg_strng in self.working_list):
            self.working_list.append(StringMessage(61, '\nТовары:'))
        if any(80 >= msg_strng.order > 70 for msg_strng in self.working_list):
            self.working_list.append(StringMessage(70, '\nДанные доставки:'))
        if any(msg_strng.order > 90 for msg_strng in self.working_list):
            self.working_list.append(StringMessage(90, '\nОплата:'))

        self.working_list.sort(key=lambda x: x.order)
        for msg_strng in self.working_list:
            message += msg_strng.message
            message += '\n'

        return message

    def add_string_to_message(self, key, value):
        value = 'Пусто' if not value else value
        if key == 'Имя' and not any(string_message.order == 5 for string_message in self.working_list):
            self.client_name = value
            return StringMessage(5, 'Имя: {}'.format(value))
        elif key == 'phone':
            return StringMessage(10, 'Телефон: {}'.format('8' + value[1:] if value[0] == '7' else value))
        elif key == 'Тип здания':
            return StringMessage(15, 'Тип здания: {}'.format(value))
        elif key == 'Заказ на ближайшее возможное время':
            return StringMessage(20, 'Заказ на ближайшее возможное время: {}'.format('Да' if value != 'false' and value != '0' and value != '' and value != 'Пусто' else 'Нет'))
        elif key == 'Временной интервал доставки':
            return StringMessage(25, 'Временной интервал доставки: {}'.format(value))
        elif key == 'Комментарий':
            return StringMessage(30, 'Комментарий: {}'.format(value))
        elif key == 'Мне нужны приборы':
            return StringMessage(35, 'Мне нужны приборы: {}'.format('Да' if value != 'false' and value != '0' and value != '' and value != 'Пусто' else 'Нет'))
        elif key == 'Сколько приборов Вам положить':
            return StringMessage(40, 'Количество приборов: {}'.format(value))
        elif key == 'Я хочу, чтобы мне подтвердили заказ через:':
            return StringMessage(45, 'Я хочу, чтобы мне подтвердили заказ через: {}'.format(value))
        elif key == 'Форма оплаты':
            return StringMessage(50, 'Форма оплаты: {}'.format(value))
        elif key == 'С какой суммы Вам нужна сдача?':
            return StringMessage(55, 'С какой суммы Вам нужна сдача?: {}'.format(value))
        elif key == 'Ближайшее метро':
            return StringMessage(60, 'Ближайшее метро: {}'.format(value))
        elif key == 'records':
            self.unpack_sublist('records')
        elif key == 'shipping_fields':
            self.unpack_sublist('shipping_fields')
        elif key == 'order_number':
            self.working_list.append(StringMessage(0, 'Новая заявка №{}\n'.format(value)))
            return StringMessage(95, 'Счет: №{}'.format(value))
        elif key == 'budget':
            return StringMessage(100, 'Бюджет: {} RUB'.format(value))
        elif key == 'Адрес':
            return StringMessage(80, 'Адрес: {}'.format(value))
        elif key == 'Опции доставки':
            return StringMessage(75, 'Опции доставки: {}'.format(value))
        elif key == 'offers':
            self.form_bucket()
        elif key == 'shipping_price':
            return StringMessage(65, 'Доставка: {}'.format(value))
        else:
            return None

    def unpack_sublist(self, sublist_name):
        for item in self.dict[sublist_name]:
            result_string = self.add_string_to_message(item['title'], item['value'])
            if result_string is not None:
                self.working_list.append(result_string)

    def unpack_subdict(self, subdict_name):
        for key, value in self.dict[subdict_name].items():
            result_string = self.add_string_to_message(key, value)
            if result_string is not None:
                self.working_list.append(result_string)

    def form_bucket(self):
        bucket_list = self.dict['offers']
        item_list = []
        shop_dict = spreadsheet_sync.goods_dict
        for item in bucket_list:
            self.weight += float(item['weight']) * int(item['amount'])
            item['title'] = item['title'].replace('\n', '').replace('  ', ' ').replace('\t', '')
            while item['title'][-1] == ' ':
                item['title'] = item['title'][:-1]
            item_list.append([item, list(self.get_shop(item['title'], shop_dict))])
        self.weight = math.ceil(self.weight * 100)/100
        self.working_list.append(StringMessage(85, 'Общий вес: {} кг.\n'.format(self.weight)))
        definite_shop_list = [value[0] for key, value in item_list if len(value) == 1]
        for i in range(len(item_list)):
            if any(shop_item in definite_shop_list for shop_item in item_list[i][1]):
                item_list[i][1] = [shp_item for shp_item in item_list[i][1] if shp_item in definite_shop_list][0]
            else:
                item_list[i][1] = '/'.join(item_list[i][1])
        shops_dict = {}
        for key, value in item_list:
            if value in shops_dict:
                shops_dict[value].append(key)
            else:
                shops_dict[value] = [key]

        for key, value in shops_dict.items():
            shop_order = ''
            shop_order += '{}\n-------------\n'.format(key + ' (❗Нет телеграмма)' if key in spreadsheet_sync.chat_dict and spreadsheet_sync.chat_dict[key] is None else key)
            for item in value:
                shop_order += '{}, {} шт., {} RUB\n'.format(item['title'], item['amount'], item['budget'])
                if 'options' in item:
                    shop_order += '  ({})\n'.format(', '.join(item['options']))

            result_string = StringMessage(62, shop_order)
            self.working_list.append(result_string)

    def form_working_list(self):
        for key, value in self.dict.items():
            result_string = self.add_string_to_message(key, value)
            if result_string is not None:
                self.working_list.append(result_string)

    def form_keyboard(self):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Отослать в магазин', callback_data='send-to-store'),
                     telebot.types.InlineKeyboardButton(text='Начать чат с клиентом', callback_data='client_notice'))
        keyboard.add(telebot.types.InlineKeyboardButton(text='Открыть страницу заказа', url='http://taplink.cc/vegandelivery/m/'))
        return keyboard

    def get_shop(self, item_name, shop_dict):
        for key, value in shop_dict.items():
            if item_name in value:
                yield key


class BucketForShops:

    def __init__(self, order_text):
        self.goods_dict = spreadsheet_sync.goods_dict
        if 'Магазины оповещены' in order_text:
            self.stores_noticed = True
        else:
            self.stores_noticed = False
        if 'Клиент оповещен' in order_text or 'Клиент не найден' in order_text:
            self.client_noticed = True
        else:
            self.client_noticed = False
        if 'Товары' in order_text:
            goods_string = order_text[order_text.index('Товары') + len('Товары:\n'):]
            goods_data = [item.split('\n-------------\n') for item in goods_string.split('\n\n') if '-------------' in item]
            self.goods_dict = {item[0].replace(' (❗Нет телеграмма)', ''): item[1] for item in goods_data}
            self.price_dict = {item[0].replace(' (❗Нет телеграмма)', ''): self.get_sum(item[1]) for item in goods_data}
        self.check_num = order_text[order_text.index('Счет: №') + len('Счет: №'):].split()[0]
        self.phone = order_text[order_text.index('Телефон:') + len('Телефон:'):].split()[0] if 'Телефон:' in order_text else 'None'
        self.name = order_text[order_text.index('Имя: ') + len('Имя: '):order_text.index('\nТелефон:')]  if 'Телефон:' in order_text and 'Имя: ' in order_text else 'None'
        self.contact = order_text[order_text.index('Я хочу, чтобы мне подтвердили заказ через:') + len('Я хочу, чтобы мне подтвердили заказ через:'):].split()[0] if 'Я хочу, чтобы мне подтвердили заказ через:' in order_text else None

    def get_sum(self, item_list):
        strings = item_list.split('\n')
        total = 0
        for strng in strings:
            if 'RUB' in strng.split():
                total += int(strng.split()[-2])
        return total

    def form_keyboard(self, stores_sent=False, client_sent=False):
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(telebot.types.InlineKeyboardButton(text='Отослать в магазин' if not self.stores_noticed and not stores_sent else '✅ Послано в магазин',
                                                        callback_data='send-to-store' if not self.stores_noticed and not stores_sent else 'sent'),
                     telebot.types.InlineKeyboardButton(
                         text='Начать чат с клиентом' if not self.client_noticed and not client_sent else '✅ Оповещение выслано',
                         callback_data='client_notice' if not self.client_noticed and not client_sent else 'client_sent')
                     )
        keyboard.add(telebot.types.InlineKeyboardButton(text='Открыть страницу заказа',
                                                        url='https://taplink.cc/brodelivery.ru'))
        return keyboard

    def reply_to_store(self, call):
        if not self.goods_dict:
            return False, call.message.text, telebot.types.InlineKeyboardMarkup(row_width=2)
        call_data = call.data.split('_')
        stores_to_choose = [key for key in self.goods_dict.keys() if '/' in key]
        if call_data[0] == 'cancel':
            keyboard = self.form_keyboard()
            return False, call.message.text.replace('\nВыберите магазин:', ''), keyboard
        elif call_data[0] == 'sent':
            return None
        elif len(call_data) - 1 < len(stores_to_choose):
            choosing_store = stores_to_choose[len(call_data)-1]
            choice = choosing_store.split('/')

            keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
            buttons = []
            for shop in choice:
                buttons.append(telebot.types.InlineKeyboardButton(text=shop, callback_data=call.data + '_' + shop))
            keyboard.row(*buttons)
            keyboard.add(telebot.types.InlineKeyboardButton(text='Отмена', callback_data='cancel'))

            return False, call.message.text, keyboard
        else:
            chosen_shop_list = call.data.split('_')[1:]
            for key, value in self.goods_dict.items():
                if '/' in key:
                    chosen_shop = next(shop for shop in chosen_shop_list if shop in key.split('/'))
                    call.message.text = call.message.text.replace(key, chosen_shop)
                    self.goods_dict[chosen_shop] = self.goods_dict[key]
                    self.price_dict[chosen_shop] = self.price_dict[key]
                    del self.goods_dict[key]
                    del self.price_dict[key]

            return True, self, call.message.text + '\nМагазины оповещены', self.form_keyboard(stores_sent=True)

    def get_notice(self):
        return self.contact, self.phone,\
               'Здравствуйте, {}! ☀️\nПолучили Ваш заказ. Сейчас мы уточним наличие позиций у кафе, и вернёмся к Вам! 🌱'.format(self.name),\
               self.name + ' Счет №{}'.format(self.check_num)

    def form_message(self, shop_name, call):
        order_text = call.message.text
        message = ' 🥑!!Новый заказ!! 🥑\n'
        message += 'Счет №{}\n\n'.format(self.check_num)
        message += self.goods_dict[shop_name]
        message += '\nСумма: {} RUB'.format(self.price_dict[shop_name])
        if 'Мне нужны приборы: Да' in order_text:
            if 'Количество приборов' in order_text:
                forks_number = order_text[order_text.index('Количество приборов:') + len('Количество приборов:'):].split()[0]
                message += '\n\nКоличество приборов: {}'.format(forks_number)
            else:
                message += '\n\nНужны приборы.'

        else:
            message += '\n\nПриборы не нужны.'

        message += '\n\nПодтвердите, пожалуйста, наличие позиций.'
        return message


class StringMessage:
    def __init__(self, order, message):
        self.order = order
        self.message = message


class StopList:
    def __init__(self, chat_id, admin_mode=False):
        spreadsheet_sync.get_shops()
        self.name = next(key for key, value in spreadsheet_sync.chat_dict.items() if value == chat_id)
        self.goods = spreadsheet_sync.goods_dict[self.name]
        with open('stoplist.pkl', 'rb') as f:
            self.stop_list = pickle.load(f)
        self.banned_goods = [item for item in self.goods if item in self.stop_list]
        self.unbanned_goods = []
        self.pages = list(self.form_pages(9))
        self.admin_mode = admin_mode
        self.chat_id = chat_id if not admin_mode else 197216910

    def form_pages(self, n):
        for i in range(0, len(self.goods), n):
            # Create an index range for l of n items:
            yield self.goods[i:i + n]

    def send_stop_list_page(self, page_num, message_id=None):
        page = self.pages[page_num]
        keyboard = telebot.types.InlineKeyboardMarkup()
        for good in page:
            if good not in self.banned_goods:
                keyboard.add(telebot.types.InlineKeyboardButton(text='\n{} {}'.format('✅',  good[:45]),
                                                                callback_data='stoplist_ban_' + str(self.goods.index(good)) + '_' + str(page_num)))
            else:
                keyboard.add(telebot.types.InlineKeyboardButton(text='\n{} {}'.format('⛔️', good[:45]),
                                                                callback_data='stoplist_unban_' + str(self.goods.index(good)) + '_' + str(page_num)))
        buttons = []
        if page_num > 0:
            buttons.append(telebot.types.InlineKeyboardButton(text='⬅️', callback_data='stoplist_page_' + str(page_num-1)))
        else:
            buttons.append(telebot.types.InlineKeyboardButton(text='⏺', callback_data='-'))
        buttons.append(telebot.types.InlineKeyboardButton(text='стр.' + str(page_num + 1), callback_data='-'))
        if len(self.pages) - 1 > page_num:
            buttons.append(telebot.types.InlineKeyboardButton(text='➡️', callback_data='stoplist_page_' + str(page_num+1)))
        else:
            buttons.append(telebot.types.InlineKeyboardButton(text='⏺', callback_data='-'))
        keyboard.add(*buttons)
        keyboard.add(telebot.types.InlineKeyboardButton(text='Принять',
                                                        callback_data='stoplist_commit'))
        text = 'Редактирование стоплиста "{}"'.format(self.name)

        if message_id is None:
            bot_methods.send_message(self.chat_id, text, reply_markup=keyboard)
        else:
            bot_methods.edit_message(self.chat_id, message_id, text, reply_markup=keyboard)

    def ban_item(self, index):
        item = self.goods[index]
        if item not in self.banned_goods:
            self.banned_goods.append(item)
        if item in self.unbanned_goods:
            self.unbanned_goods.remove(item)

    def unban_good(self, index):
        item = self.goods[index]
        if item in self.banned_goods:
            self.banned_goods.remove(item)
            self.unbanned_goods.append(item)

    def process_callback(self, call):
        call_data = call.data.split('_')
        if call_data[1] == 'page':
            page_num = int(call_data[2])
            self.send_stop_list_page(page_num, message_id=call.message.message_id)
        elif call_data[1] == 'ban':
            page_num = int(call_data[-1])
            item_index = int(call_data[-2])
            self.ban_item(item_index)
            self.send_stop_list_page(page_num, message_id=call.message.message_id)
        elif call_data[1] == 'unban':
            page_num = int(call_data[-1])
            item_index = int(call_data[-2])
            self.unban_good(item_index)
            self.send_stop_list_page(page_num, message_id=call.message.message_id)
        elif call_data[1] == 'commit':
            self.commit(call)

    def commit(self, call):
        message = 'Изменения стоп-листа приняты.\n'
        self.banned_goods = [item for item in self.banned_goods if item not in self.stop_list]
        if self.banned_goods:
            selenium_main.pending_stoplist.append(self.banned_goods)
            message += '\nТовары в стоп-листе:\n'
            for item in self.banned_goods:
                message += '   ' + str(item) + '\n'
        if self.unbanned_goods:
            selenium_main.pending_releases.append(self.unbanned_goods)
            selenium_main.pending_stoplist.append(self.banned_goods)
            message += '\nИз стоп-листа удалены:\n'
            for item in self.unbanned_goods:
                message += '   ' + str(item) + '\n'

        bot_methods.edit_message(self.chat_id, call.message.message_id, message)
        del redacting_stoplists[self.chat_id]

