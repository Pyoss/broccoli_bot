import gspread
from oauth2client.service_account import ServiceAccountCredentials

chat_dict = {}


def get_shops():
    # use creds to create a client to interact with the Google Drive API
    scope = ['https://spreadsheets.google.com/feeds',
             'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('VeganPartnersSheetKey.json', scope)
    client = gspread.authorize(creds)

    # Find a workbook by name and open the first sheet
    # Make sure you use the right name here.
    sheet = client.open("Брокколи Партнер").sheet1

    full_list = sheet.get_all_values()
    shop_dict = {}
    i = 0
    while i < len(full_list[0]):
        try:
            shop_name = full_list[0][i]
            chat_dict[shop_name] = int(full_list[1][i])
            shop_item_names = []
            for lst in full_list[2:]:
                if lst[i] != '':
                    shop_item_names.append(lst[i])
            shop_dict[shop_name] = shop_item_names
            i += 1
        except:
            i += 1
    return shop_dict

goods_dict = get_shops()
print(goods_dict)