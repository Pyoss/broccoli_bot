import gspread
from oauth2client.service_account import ServiceAccountCredentials

chat_dict = {'Falafel Bro Маяковская': -262347442,
             'Falafel Bro Марксистская': -373838315,
             'Holy Vegan': -365554948,
             'Rabbits Room': -361477504,
             'Raw to go Депо': -396281204,
             'SML Cafe': -321111085,
             'Veganga + Сладенький': -301410097,
             'Балифорния': -321104542,
             'Добрая Кухня': -301838854,
             'Зеленый Лис': -250723953,
             'Ra Family': -397061161,
             'Слайс Пицца': -167912698,
             'Маллакто + FungFung': -293184099,
             'VegU': -334936889,
             'NYM Kitchen': -353559775,
             'Угол': -222417832,
             'Горох': -376544620,
             'Мох Волна': -368218918}


def get_shops():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('VeganPartnersSheetKey.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("тест таблица").sheet1

    full_list = sheet.get_all_values()
    shop_dict = {}
    i = 0
    while i < len(full_list[0]):
        shop_name = full_list[0][i]
        shop_item_names = []
        for lst in full_list[2:]:
            if lst[i] != '':
                shop_item_names.append(lst[i])
        shop_dict[shop_name] = shop_item_names
        i += 1
    return shop_dict

goods_dict = get_shops()
print(goods_dict)