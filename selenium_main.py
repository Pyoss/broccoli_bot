from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
import time
import pickle
import threading
import bot_methods
import traceback
from datetime import datetime
import spreadsheet_sync


pending_stoplist = []
pending_releases = []

def check_login():
    options = Options()
    options.headless = True
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
    bot_methods.send_message(197216910, 'Активация драйвера завершена.')
    driver.get('https://taplink.ru/profile/auth/signin/')
    bot_methods.send_message(197216910, 'Авторизация на сайте...')
    login(driver)

    bot_methods.send_message(197216910, 'Авторизация завершена...')
    return driver


def head_login():
    driver = webdriver.Chrome(ChromeDriverManager().install())
    bot_methods.send_message(197216910, 'Активация драйвера завершена.')
    driver.get('https://taplink.ru/profile/auth/signin/')
    bot_methods.send_message(197216910, 'Авторизация на сайте...')
    login(driver)

    bot_methods.send_message(197216910, 'Авторизация завершена...')
    return driver


def find_element(driver, element_css_name):
    try:
        element = WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, element_css_name)))
        return element
    except TimeoutException:
        driver.quit()
        raise Exception('{}'.format(element_css_name))


def find_elements(driver, element_css_name):
    try:
        elements = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, element_css_name)))
        return elements
    except TimeoutException:
        return []


def login(driver):
    username = find_element(driver, "input[type='email']")
    password = find_element(driver, "input[type='password']")

    username.send_keys("yisgit@gmail.com")
    password.send_keys("334ab7f2c")
    find_element(driver, "button[type='submit']").click()
    driver.get('https://taplink.ru/profile/1017970/account/access/shared/')
    elements = find_elements(driver, "button[class='button is-primary is-small']")
    elements[0].click()
    return driver


def check_archive(driver, item):
    driver.get('https://taplink.ru/profile/924521/products/archive/')
    search_field = find_element(driver, "input[type='search']")
    search_field.send_keys(item)
    time.sleep(2)
    bot_methods.send_message(197216910, 'Проверка есть ли {} в архиве.'.format(item))
    try:
        elements = find_elements(driver, "td[data-label='Название']")
        for element in elements:
            name = element.text
            if name == item:
                driver.get('https://taplink.ru/profile/924521/products/active/')
                bot_methods.send_message(197216910, '{} найден в архиве.'.format(item))
                return True
        driver.get('https://taplink.ru/profile/924521/products/active/')
        return False
    except Exception as e:
        driver.get('https://taplink.ru/profile/924521/products/active/')
        bot_methods.send_message(197216910, str(traceback.format_exc())[-300:])
        return False


def add_to_archive(driver, item_list, additional=False):
    print(item_list)
    bot_methods.send_message(197216910, 'Перемещение в архив.')
    try:
        with open('stoplist.pkl', 'rb') as f:
            stoplist_for_pickle = pickle.load(f)
    except:
        stoplist_for_pickle = []
    not_found = []
    for item in item_list:
        try:
            driver.get('https://taplink.ru/profile/924521/products/active/')
            found = False
            search_field = find_element(driver, "input[type='search']")
            search_field.send_keys(item)
            time.sleep(2)
            elements = find_elements(driver, "td[data-label='Название']")
            for element in elements:
                name = element.text
                if name == item:
                    found = True
                    find_element(element, "label[class='b-checkbox checkbox']").click()
                    find_element(driver, "button[class='button is-dark is-fullwidth']").click()
                    time.sleep(3)
                    buttons = find_elements(driver, "a[class='dropdown-item']")
                    buttons[0].click()
                    bot_methods.send_message(197216910, '{} успешно перемещен в архив.'.format(item))
                    if item not in stoplist_for_pickle:
                        stoplist_for_pickle.append(item)
                    break
            if not found and item not in stoplist_for_pickle:
                if check_archive(driver, item):
                    bot_methods.send_message(197216910, '❗️Товар {} уже в архиве!'.format(item))
                    if item not in stoplist_for_pickle:
                        stoplist_for_pickle.append(item)
                else:
                    not_found.append(item)
                    bot_methods.send_message(197216910, '❗️Товар {} не найден в магазине!'.format(item))
        except Exception as e:
            bot_methods.send_message(197216910, '❗️Товар {} не найден!'.format(item))
            bot_methods.send_message(197216910, str(traceback.format_exc())[-300:])
    with open('stoplist.pkl', 'wb') as f:
        pickle.dump(stoplist_for_pickle, f)

    if not additional and not_found:
        add_to_archive(driver, not_found, additional=True)

    bot_methods.send_message(197216910, 'Добавление в архив завершено.')


def remove_from_archive(driver, item_list, additional=False):
    try:
        with open('stoplist.pkl', 'rb') as f:
            stoplist_for_pickle = pickle.load(f)
    except:
        stoplist_for_pickle = []

    not_found = []
    for item in list(item_list):
        try:
            found = False
            driver.get('https://taplink.ru/profile/924521/products/archive/')
            search_field = find_element(driver, "input[type='search']")
            search_field.send_keys(item)
            time.sleep(2)
            elements = find_elements(driver, "td[data-label='Название']")
            for element in elements:
                if found:
                    pass
                name = element.text
                if name == item:
                    find_element(element, "label[class='b-checkbox checkbox']").click()
                    find_element(driver, "button[class='button is-dark is-fullwidth']").click()
                    time.sleep(3)
                    buttons = driver.find_elements_by_css_selector("a[class='dropdown-item'")
                    buttons[0].click()
                    bot_methods.send_message(197216910, '{} успешно перемещен в актив.'.format(item))
                    if item in stoplist_for_pickle:
                        stoplist_for_pickle.remove(item)
            if not found and item in stoplist_for_pickle:
                bot_methods.send_message(197216910, '❗️Товар {} не найден в архиве!'.format(item))
                not_found.append(item)
        except Exception as e:
            bot_methods.send_message(197216910, '❗️Товар {} не найден в архиве!'.format(item))
            bot_methods.send_message(197216910, str(traceback.format_exc())[-300:])
    with open('stoplist.pkl', 'wb') as f:
        pickle.dump(stoplist_for_pickle, f)

    if not additional and not_found:
        remove_from_archive(driver, not_found, additional=True)
    bot_methods.send_message(197216910, 'Добавление в актив завершено.')


def open_options(driver, item):
    driver.get('https://taplink.ru/profile/924521/products/active/')
    found = False
    search_field = find_element(driver, "input[type='search']")
    search_field.send_keys(item)
    time.sleep(2)
    elements = find_elements(driver, "td[data-label='Название']")
    for element in elements:
        name = element.text
        if name == item:
            element.click()
            element = find_element(driver, "ul[class='nav nav-tabs has-text-left']")
            time.sleep(3)
            elements = find_elements(element, "li")
            for element in elements:
                print(element.text)
                if element.text == 'ОПЦИИ':
                    element.click()


def remove_options(driver, option_names):
    item_rows = find_elements(driver, 'div[class="item-row row"]')
    for item_row in item_rows[1:]:
        text = find_element(item_row, 'input[class="input"]').get_attribute('value')
        if text in option_names:
            find_element(item_row, 'button[type="button"]').click()
            find_element(driver, 'button[class="button is-danger"]').click()


def clear_stoplist():
    with open('stoplist.pkl', 'rb') as f:
        stoplist_for_pickle = pickle.load(f)
    driver = check_login()
    remove_from_archive(driver, stoplist_for_pickle)


def start_stoplist_loop():
    print('Селениум активирован')
    def stoplist_loop():
        notified = False
        while True:
            x = datetime.now()
           # if x.hour == 6 and not notified:
           #     for value in spreadsheet_sync.chat_dict.values():
           #         message = 'Доброе утро! ☀\n' \
           #                   'Уважаемые коллеги, просим вас актуализировать ⛔️стоп-лист к моменту вашего открытия. 🕒\n\n'\
           #                   'Для того, чтобы вызвать меню стоп-листов, пожалуйста, используйте команду /stoplist\n\n'\
           #                   'Желаем вам продуктивного дня 🍀'
           #         bot_methods.send_message(value, message)
           #     notified = True
           # elif x.hour == 7 and notified:
           #     notified = False
            try:
                if pending_stoplist or pending_releases:
                    driver = check_login()
                    while pending_stoplist:
                        print(pending_stoplist[-1])
                        new_stoplist = pending_stoplist.pop()
                        add_to_archive(driver, new_stoplist)
                    while pending_releases:
                        new_releases = pending_releases.pop()
                        remove_from_archive(driver, new_releases)
                    driver.quit()
                    time.sleep(180)
            except Exception:
                bot_methods.send_message(197216910, str(traceback.format_exc())[-300:])
            time.sleep(180)

    stop_loop = threading.Thread(target=stoplist_loop)
    stop_loop.daemon = True
    stop_loop.start()

if __name__ != '__main__':
    start_stoplist_loop()
else:
    driver = head_login()
    open_options(driver, 'Фалафель с сыром')
    remove_options(driver, ['Тофу'])


