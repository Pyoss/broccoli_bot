from telethon import TelegramClient, sync
from telethon.tl.types import InputPhoneContact
from telethon.tl.functions.contacts import ImportContactsRequest, GetContactsRequest
from telethon.errors import SessionPasswordNeededError

# Use your own values here
api_id = 738628
api_hash = 'b377ab6c3b9c13deb170c2c79ff60231'


class Client_Notice:
    def __init__(self, text, phone, name):
        self.phone = phone
        self.text = text
        self.name = name

    def pulled_notice(self):
        try:
            print('process_started')
            client = TelegramClient('VeganLogin', api_id, api_hash)
            with client:
                result = client(GetContactsRequest(
                    hash=0
                ))
                for user in result.users:
                    if user.phone == self.phone:
                        user_id = user.id
                        client.send_message(user_id, self.text)
                        send = True
                        return send
                contact = InputPhoneContact(client_id=0, phone=self.phone, first_name=self.name, last_name="")
                result = client(ImportContactsRequest([contact]))
                if len(result.imported):
                    user_id = result.imported[0].user_id
                    client.send_message(user_id, self.text)
                    send = True
                    return send
        except Exception as e:
            pass



def notice_client(text, phone, name):
    print('process_started')
    client = TelegramClient('VeganLogin', api_id, api_hash)
    with client:
        result = client(GetContactsRequest(
            hash=0
        ))
        for user in result.users:
            if user.phone == phone:
                user_id = user.id
                client.send_message(user_id, text)
                send = True
                return send
        contact = InputPhoneContact(client_id=0, phone=phone, first_name=name, last_name="")
        result = client(ImportContactsRequest([contact]))
        if len(result.imported):
            user_id = result.imported[0].user_id
            client.send_message(user_id, text)
            send = True
            return send
