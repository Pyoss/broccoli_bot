#!/usr/bin/env python
# -*- coding: utf-8 -*-

import telebot
import spreadsheet_sync
import math


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
        if key == 'Имя':
            self.client_name = value
            return StringMessage(5, 'Имя: {}'.format(value))
        elif key == 'phone':
            return StringMessage(10, 'Телефон: {}'.format('8' + value[1:] if value[0] == '7' else value))
        elif key == 'Тип здания':
            return StringMessage(15, 'Тип здания: {}'.format(value))
        elif key == 'Заказ на ближайшее возможное время':
            return StringMessage(20, 'Заказ на ближайшее возможное время: {}'.format('Да' if value != 'false' and value != '0' and value != '' and value != 'Пусто' else 'Нет'))
        elif key == 'Временное интервал доставки':
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
            goods_string = order_text[order_text.index('Товары:\n') + len('Товары:\n'):]
            goods_data = [item.split('\n-------------\n') for item in goods_string.split('\n\n') if '-------------' in item]
            self.goods_dict = {item[0].replace(' (❗Нет телеграмма)', ''): item[1] for item in goods_data}
            self.price_dict = {item[0].replace(' (❗Нет телеграмма)', ''): self.get_sum(item[1]) for item in goods_data}
        self.check_num = order_text[order_text.index('Счет: №') + len('Счет: №'):].split()[0]
        self.phone = order_text[order_text.index('Телефон:') + len('Телефон:'):].split()[0]
        self.name = order_text[order_text.index('Имя: ') + len('Имя: '):order_text.index('\nТелефон:')]
        self.contact = order_text[order_text.index('Я хочу, чтобы мне подтвердили заказ через:') + len('Я хочу, чтобы мне подтвердили заказ через:'):].split()[0]

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


new_dict = {'data[order_number]': ['303'], 'data[date_created]': ['2019-04-25'], 'data[order][budget]': ['1400'], 'data[order][purpose]': ['@vegandelivery'], 'data[purpose]': ['@vegandelivery'], 'data[order][order_id]': ['653276'], 'data[shipping_fields][1][value]': ['12'], 'data[records][1][value]': ['79296052405'], 'data[offers][1][title]': ['Сэндвич с авокадо и черникой'], 'data[records][5][title]': ['Я хочу, чтобы мне подтвердили заказ через:'], 'data[records][5][value]': ['Telegram'], 'data[order_version]': ['0'], 'data[currency_code]': ['RUB'], 'data[shipping_fields][0][title]': ['Опции доставки'], 'data[order][order_status_id]': ['1'], 'data[records][2][type]': ['9'], 'data[order][tms_modify]': ['2019-04-25 22:45:34'], 'data[utm_campaign]': [''], 'data[records][5][type]': ['8'], 'data[offers][0][amount]': ['2'], 'data[email]': [''], 'data[shipping_fields][1][key]': ['addr1'], 'data[offers][1][amount]': ['1'], 'data[shipping_fields][0][key]': ['shipping_method'], 'data[utm_medium]': [''], 'data[records][6][type]': ['9'], 'data[page_link]': ['http://taplink.cc/vegandelivery/m/'], 'data[offers][1][offer_id]': ['981302'], 'data[block_id]': [''], 'data[utm_term]': [''], 'data[currency_title]': ['₽'], 'data[records][2][title]': ['Тип здания'], 'data[records][2][value]': ['Бизнес-центр'], 'data[records][3][value]': ['1'], 'data[records][3][type]': ['10'], 'data[records][0][value]': ['Тест Бота'], 'data[shipping_fields][1][title]': ['Адрес'], 'data[phone]': ['79296052405'], 'data[tms_created]': ['2019-04-25 22:45:34'], 'data[records][6][title]': ['Форма оплаты'], 'data[order][currency_code]': ['RUB'], 'data[offers][0][price]': ['350'], 'data[offers][1][budget]': ['350'], 'data[offers][0][offer_id]': ['981300'], 'data[order_id]': ['653276'], 'action': ['leads.created'], 'data[tms_modify]': ['2019-04-25 22:45:34'], 'data[shipping_price]': ['350'], 'data[utm_source]': [''], 'data[offers][1][weight]': ['0.175'], 'data[ip]': ['5.35.108.149'], 'data[order][order_version]': ['0'], 'data[page_title]': ['Товары'], 'data[fullname]': ['Тест Тестович'], 'data[records][1][title]': ['Телефон'], 'data[profile_id]': ['845465'], 'data[order_status_id]': ['1'], 'data[records][1][type]': ['7'], 'data[offers][1][price]': ['350'], 'data[nickname]': ['vegandelivery'], 'data[offers][0][budget]': ['700'], 'data[lead_id]': ['966714'], 'data[shipping_fields][0][value]': ['Платная доставка (точную сумму подскажет менеджер)'], 'data[offers][0][title]': ['Сэндвич фиолетовый хумус'], 'data[records][4][value]': ['1'], 'data[budget]': ['1400'], 'data[records][4][type]': ['10'], 'data[records][4][title]': ['Мне нужны приборы'], 'data[records][6][value]': ['Наличный'], 'data[order][currency_title]': ['₽'], 'data[lead_number]': ['303'], 'data[records][0][type]': ['3'], 'data[order][order_number]': ['303'], 'data[offers][0][weight]': ['0.155'], 'data[records][3][title]': ['Заказ на ближайшее возможное время'], 'data[contact_id]': ['700510'], 'data[records][0][title]': ['Имя']}

