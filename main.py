import telebot
from telebot import types
import requests
import bs4
import csv
#from config_new import *
import os
import os.path

CNT = 0
#  списки для хранения параметров
PRICE_NOW = []

PRICE_OLD = []

HREF = []

TOWN = []

ITEM = []

CATEGORY = []

bot = telebot.TeleBot(TG_TOKEN)


class Avito_parser_main(object):
    '''
    класс отвечающий за парсинг авито с параметрами
    '''

    def __init__(self, categories, town, price_now=None, price_old=None, item=None):
        self.BASE_URL = BASE_URL
        self.url = requests.get(self.get_url(categories, town)).url
        self.item = item
        if self.item:
            self.url_r = requests.get(self.get_url(categories, town), params={'q': self.item}).text

        else:
            self.url_r = requests.get(self.get_url(categories, town)).text
        self.price_now = price_now
        self.price_old = price_old
        self.params = {}
        self.session = requests.Session()
        self.headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

    def get_url(self, category, town):
        '''
        Получаем url с городом и категорией
        :param category:
        :param town:
        :return:
        '''
        url_address = self.BASE_URL + str(self.Towner_and_Item(town) + '/' + str(self.Towner_and_Item(category)))
        print(url_address)
        return url_address

    def get_pagination(self, text):
        '''
        получение количества страниц
        :param text:
        :return:
        '''
        try:
            soup = bs4.BeautifulSoup(text, 'html.parser')
            pagiantion = soup.select('div.pagination-root-2oCjZ')
            for i in pagiantion:
                page = i.select('span', attrs={'class': 'pagination-item-1WyVp'})[-2].text.strip()

            return page

        except Exception as e:
            print(repr(e))
            pass

    def parametring(self, page, item=None):
        '''
        Задание параметров в ссылке
        :param page:
        :param item:
        :return:
        '''
        if page >= 1 and item:
            self.params['q'] = item
            self.params['p'] = page
            result = self.session.get(url=self.url, params=self.params)

        if page >= 1:
            self.params['p'] = page
            result = self.session.get(url=self.url, params=self.params)

        else:
            result = self.session.get(url=self.url, params=self.params)

        return result

    def parsing_block(self, result):
        '''
        Парсинг страницы : парсинг названия , адреса , цены , ссылки
        :param result:
        :return:
        '''
        data_all = []
        print(result.url)
        soup = bs4.BeautifulSoup(result.text, 'html.parser')
        block = soup.select(
            'div.snippet-horizontal.item.item_table.clearfix.js-catalog-item-enum.item-with-contact.js-item-extended')

        for el in block:
            try:
                title = el.select_one('a.snippet-link').text.strip()

            except:
                title = ' '

            try:
                href = (str('https://www.avito.ru/') + str(el.select_one('a.snippet-link')['href'])).strip()

            except:
                href = ' '

            price = el.select_one('span.snippet-price').text.strip().replace('₽', 'руб')
            try:
                # сравнение цены товара с той которую задал пользователь
                if self.price_now and self.price_old:
                    pri_ce = self.number(price[:-5])
                    if int(self.price_now) <= int(pri_ce) <= int(self.price_old):
                        price = el.select_one('span.snippet-price').text.strip().replace('₽', 'руб')

                    else:
                        price = ''

                elif self.price_now:
                    pri_ce = self.number(price[:-5])
                    if int(self.price_now) <= int(pri_ce):
                        price = el.select_one('span.snippet-price').text.strip().replace('₽', 'руб')

                    else:
                        price = ''

                elif self.price_old:
                    pri_ce = self.number(price[:-5])
                    if int(pri_ce) <= int(self.price_old):
                        price = el.select_one('span.snippet-price').text.strip().replace('₽', 'руб')

                    else:
                        price = ''

                else:
                    price = el.select_one('span.snippet-price').text.strip().replace('₽', 'руб')

            except:
                price = 'Цена не указана'

            try:
                address = el.select_one('span.item-address-georeferences-item__content').text.strip()

            except:
                address = ' '

            try:
                if price == '':
                    pass

                else:
                    data = {
                        'title': title,
                        'href': href,
                        'price': price,
                        'address': address
                    }
                    data_all.append(data)
            except:
                pass

        print(data_all)
        return data_all

    def csv_writer(self, data):
        '''
        Запись словаря data из parsing_block в csv
        :param data:
        :return:
        '''
        with open('text.csv', 'a') as f:
            writer = csv.writer(f)
            for i in data:
                writer.writerow((i['title'],
                                 i['href'],
                                 i['price'],
                                 i['address']))

    def Towner_and_Item(self, Town):
        '''
        Перевод русской речи на английскую , для того чтобы можно было задать параметры для ссылки
        :param Town:
        :return:
        '''
        result = Town.lower()
        res = ''
        for i in result:
            res += dict_ru_en[i]

        return res

    def number(self, numb):
        '''
        Переформирование строковых значений
        :param numb:
        :return:
        '''
        res = [i for i in numb]
        result = ''
        for i in res:
            if i != ' ':
                result += i

        return result


class Avito_href(Avito_parser_main):
    '''
    Класс отвечающий за парсинг с ссылки без параметров
    '''

    def __init__(self, href):
        super(Avito_parser_main, self).__init__()
        self.href = href
        self.params = {}
        self.text_href = requests.get(self.href).text
        self.session = requests.Session()
        self.headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

    def parametr(self, page):
        if page >= 1:
            self.params['p'] = page
            result = self.session.get(url=self.href, params=self.params)

        else:
            result = self.session.get(url=self.href)

        return result


def main_main(town, category, item=None, price_now=None, price_old=None):
    '''
    Запуск парсера с параметрами , значения которые не ввел пользователь будут 1
    :param town:
    :param category:
    :param item:
    :param price_now:
    :param price_old:
    :return:
    '''
    if item == 1:
        item = None

    if price_now == 1:
        price_now = None

    if price_old == 1:
        price_old = None

    cls = Avito_parser_main(category, town, price_now, price_old, item)
    r = cls.url_r
    rang = cls.get_pagination(r)
    for i in range(1, int(rang) + 1):
        if item:
            text = cls.parametring(page=i, item=item)

        else:
            text = cls.parametring(page=i)

        res = cls.parsing_block(text)
        cls.csv_writer(res)


def main_href(href):
    '''
    Аналогичная функция запуска парсера без параметров
    :param href:
    :return:
    '''
    cls = Avito_href(href)
    r = cls.text_href
    rang = cls.get_pagination(r)
    for i in range(1, int(rang) + 1):
        text = cls.parametr(page=i)
        res = cls.parsing_block(text)
        cls.csv_writer(res)


@bot.message_handler(commands=['start'])
def starting(message):
    '''
    Обработчик команды start
    :param message:
    :return:
    '''
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    board_1 = types.KeyboardButton('Начать работу')
    board_2 = types.KeyboardButton('Как пользоваться')

    markup.add(board_1, board_2)
    bot.send_message(message.chat.id, GREET, parse_mode='html', reply_markup=markup)


@bot.message_handler(commands=['help'])
def helping(message):
    '''
    Обработчик комманды help
    :param message:
    :return:
    '''
    bot.send_message(message.chat.id, HELP, parse_mode='html')


@bot.message_handler(regexp=r'((https?):((//)|(\\\\))+([\w\d:#@%/;$()~_?\+-=\\\.&](#!)?)*)')  # регудярное выражение
def get_url(messsage):  # для нахождения url
    HREF.append(messsage.text.lower().strip())
    markup_illine = types.InlineKeyboardMarkup()
    board_1 = types.InlineKeyboardButton('Ок', callback_data='OK')

    markup_illine.add(board_1)

    bot.send_message(messsage.chat.id, 'Url получен', reply_markup=markup_illine)


@bot.message_handler(content_types=['text'])
def main_avito(message):
    global CNT

    if message.chat.type == 'private':
        '''
        Обработка основных комманд
        '''
        if message.text.lower().strip() == 'начать работу':
            markup_main_inline = types.InlineKeyboardMarkup()
            button_1 = types.InlineKeyboardButton('Задать параметры для поиска объявлений', callback_data='main')
            button_2 = types.InlineKeyboardButton('Ввести ссылку', callback_data='href')

            markup_main_inline.add(button_1, button_2)

            bot.send_message(message.chat.id, 'Выбери нужный вариант', reply_markup=markup_main_inline)

        elif message.text.lower().strip() == 'как пользоваться':
            bot.send_message(message.chat.id, HELP, parse_mode='html')

        else:
            # Получение параметров для парсинга , с заданием воиросов для ползователя
            if CNT == 0:
                town = message.text.lower().strip()
                TOWN.append(town)
                CNT += 1

                bot.send_message(message.chat.id,
                                 'Введите название продукта которое вам нужно найти , если не надо ставьте прочерк')

            elif CNT == 1:
                item = message.text.lower().strip()
                if item == '-':
                    item = 1

                ITEM.append(item)

                CNT += 1

                bot.send_message(message.chat.id,
                                 'Введите  минимальную цену продукта , если не надо ставьте прочерк')

            elif CNT == 2:
                price_now = message.text.lower().strip()
                if price_now == '-':
                    price_now = 1

                PRICE_NOW.append(price_now)
                CNT += 1

                bot.send_message(message.chat.id,
                                 'Введите максимальную цены продукта , если не надо ставьте прочерк')

            elif CNT == 3:
                price_old = message.text.lower().strip()
                if price_old == '-':
                    price_old = 1

                PRICE_OLD.append(price_old)
                CNT = 0

                bot.send_message(message.chat.id,
                                 'Нужные данные введены , парсинг может занять боллее 5 минут , пожалуйста имейте терпение')

                file_path = 'text.csv'

                if os.path.exists(file_path):
                    '''
                    Очистка файла 
                    '''
                    os.remove(file_path)
                    with open(file_path, 'w+') as file:
                        pass

                with open(file_path, 'rb') as file:
                    # Запись в файл работы парсера
                    try:
                        main_main(town=TOWN[-1], category=CATEGORY[-1], item=ITEM[-1], price_now=PRICE_NOW[-1],
                                  price_old=PRICE_OLD[-1])

                    except:
                        bot.send_message(message.chat.id, 'Вы ввели некорректные данные , пожалуйста повторите')

                    bot.send_document(message.chat.id, file)
                    bot.send_message(message.chat.id, 'Парсинг объявлений закончен')

                # Очитска списков , чтобы не было перенакопления
                PRICE_NOW[:] = []

                PRICE_OLD[:] = []

                HREF[:] = []

                TOWN[:] = []

                ITEM[:] = []

                CATEGORY[:] = []


@bot.callback_query_handler(func=lambda call: True)
def main_callback(call):
    if call.message:
        if call.data == 'main':
            # Вывод кнопок всех категорий
            markup_hanr = types.InlineKeyboardMarkup()
            hanr_1 = types.InlineKeyboardButton('Транспорт', callback_data='T')
            hanr_2 = types.InlineKeyboardButton('Недвижимость', callback_data='N')
            hanr_3 = types.InlineKeyboardButton('Работа', callback_data='P')
            hanr_4 = types.InlineKeyboardButton('Личные вещи', callback_data='L')
            hanr_5 = types.InlineKeyboardButton('Для дома и дачи', callback_data='D')
            hanr_6 = types.InlineKeyboardButton('Бытовая электроника', callback_data='B')
            hanr_7 = types.InlineKeyboardButton('Хобби и отдых', callback_data='X')
            hanr_8 = types.InlineKeyboardButton('Животные', callback_data='Z')
            hanr_9 = types.InlineKeyboardButton('Для бизнеса', callback_data='DX')
            markup_hanr.add(hanr_1, hanr_2, hanr_3, hanr_4, hanr_5, hanr_6, hanr_7, hanr_8, hanr_9)

            bot.send_message(call.message.chat.id, 'Выбереие категорию', reply_markup=markup_hanr)


        elif call.data == 'href':
            bot.send_message(call.message.chat.id, 'Введите url для парсинга объявлений')

        elif call.data == 'parsing':
            file_path = 'text.csv'
            if os.path.exists(file_path):
                os.remove(file_path)
                with open(file_path, 'w+') as file:
                    pass

            with open(file_path, 'rb') as file:
                try :
                    main_href(HREF[-1])

                except:
                    bot.send_message(call.message.chat.id , 'Вы ввели некоректные данные повторите еще раз пожалуйста')

                bot.send_document(call.message.chat.id, file)
                bot.send_message(call.message.chat.id, 'Парсинг объявлений закончен')

            PRICE_NOW[:] = []

            PRICE_OLD[:] = []

            HREF[:] = []

            TOWN[:] = []

            ITEM[:] = []

            CATEGORY[:] = []

        elif call.data == 'OK':
            mark = types.InlineKeyboardMarkup()
            mar_but = types.InlineKeyboardButton('Начать', callback_data='parsing')
            mark.add(mar_but)

            bot.send_message(call.message.chat.id, 'Начинается парсинг , пожалуйста подождите минут 5',
                             reply_markup=mark)

        elif call.data == 'T':
            T_markup = types.InlineKeyboardMarkup()
            T_1 = types.InlineKeyboardButton('Автомобили', callback_data='q')
            T_2 = types.InlineKeyboardButton('Мотоциклы и мототехника', callback_data='w')
            T_3 = types.InlineKeyboardButton('Грузовики и спецтехника', callback_data='e')
            T_4 = types.InlineKeyboardButton('Водный транспорт', callback_data='r')
            T_5 = types.InlineKeyboardButton('Запчасти и аксессуары', callback_data='t')

            T_markup.add(T_1, T_2, T_3, T_4, T_5)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=T_markup)

        elif call.data == 'N':
            N_markup = types.InlineKeyboardMarkup()
            N_1 = types.InlineKeyboardButton('Все квартиры', callback_data='y')
            N_2 = types.InlineKeyboardButton('Квартиры в новостройках', callback_data='u')
            N_3 = types.InlineKeyboardButton('Квартиры в аренду', callback_data='i')
            N_4 = types.InlineKeyboardButton('Квартиры посуточно', callback_data='o')
            N_5 = types.InlineKeyboardButton('Дома, дачи, коттеджи', callback_data='p')
            N_6 = types.InlineKeyboardButton('Комнаты', callback_data='a')
            N_7 = types.InlineKeyboardButton('Коммерческая недвижимость', callback_data='s')

            N_markup.add(N_1, N_2, N_3, N_4, N_5, N_6, N_7)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=N_markup)

        elif call.data == 'P':
            P_markup = types.InlineKeyboardMarkup()
            P_1 = types.InlineKeyboardButton('Вакансии', callback_data='d')
            P_2 = types.InlineKeyboardButton('Отрасли', callback_data='f')
            P_3 = types.InlineKeyboardButton('Резюме', callback_data='g')

            P_markup.add(P_1, P_2, P_3)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=P_markup)

        elif call.data == 'L':
            L_markup = types.InlineKeyboardMarkup()
            L_1 = types.InlineKeyboardButton('Одежда, обувь, аксессуары', callback_data='h')
            L_2 = types.InlineKeyboardButton('Детская одежда и обувь', callback_data='j')
            L_3 = types.InlineKeyboardButton('Товары для детей и игрушки', callback_data='k')
            L_4 = types.InlineKeyboardButton('Часы и украшения', callback_data='l')
            L_5 = types.InlineKeyboardButton('Красота и здоровье', callback_data='z')

            L_markup.add(L_1, L_2, L_3, L_4, L_5)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=L_markup)

        elif call.data == 'D':
            D_markup = types.InlineKeyboardMarkup()
            D_1 = types.InlineKeyboardButton('Бытовая техника', callback_data='x')
            D_2 = types.InlineKeyboardButton('Бытовая техника', callback_data='c')
            D_3 = types.InlineKeyboardButton('Посуда и товары для кухни', callback_data='v')
            D_4 = types.InlineKeyboardButton('Продукты питания', callback_data='b')
            D_5 = types.InlineKeyboardButton('Ремонт и строительство', callback_data='n')
            D_6 = types.InlineKeyboardButton('Растения', callback_data='m')

            D_markup.add(D_1, D_2, D_3, D_4, D_5, D_6)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=D_markup)

        elif call.data == 'B':
            B_markup = types.InlineKeyboardMarkup()
            B_1 = types.InlineKeyboardButton('Аудио и видео', callback_data='qw')
            B_2 = types.InlineKeyboardButton('Игры, приставки и программы', callback_data='er')
            B_3 = types.InlineKeyboardButton('Настольные компьютеры', callback_data='ty')
            B_4 = types.InlineKeyboardButton('Ноутбуки', callback_data='ui')
            B_5 = types.InlineKeyboardButton('Оргтехника и расходники', callback_data='op')
            B_6 = types.InlineKeyboardButton('Планшеты и электронные книги', callback_data='as')
            B_7 = types.InlineKeyboardButton('Телефоны', callback_data='df')
            B_8 = types.InlineKeyboardButton('Товары для компьютера', callback_data='gh')
            B_9 = types.InlineKeyboardButton('Фототехника', callback_data='jk')

            B_markup.add(B_1, B_2, B_3, B_4, B_5, B_6, B_7, B_8, B_9)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=B_markup)

        elif call.data == 'X':
            X_markup = types.InlineKeyboardMarkup()
            X_1 = types.InlineKeyboardButton('Билеты и путешествия', callback_data='lz')
            X_2 = types.InlineKeyboardButton('Велосипеды', callback_data='xc')
            X_3 = types.InlineKeyboardButton('Книги и журналы', callback_data='vb')
            X_4 = types.InlineKeyboardButton('Коллекционирование', callback_data='nm')
            X_5 = types.InlineKeyboardButton('Музыкальные инструменты', callback_data='qwe')
            X_6 = types.InlineKeyboardButton('Охота и рыбалка', callback_data='rty')
            X_7 = types.InlineKeyboardButton('Спорт и отдых', callback_data='uio')

            X_markup.add(X_1, X_2, X_3, X_4, X_5, X_6, X_7)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=X_markup)

        elif call.data == 'Z':
            Z_markup = types.InlineKeyboardMarkup()
            Z_1 = types.InlineKeyboardButton('Собаки', callback_data='pas')
            Z_2 = types.InlineKeyboardButton('Кошки', callback_data='dfg')
            Z_3 = types.InlineKeyboardButton('Птицы', callback_data='hjk')
            Z_4 = types.InlineKeyboardButton('Аквариум', callback_data='lzx')
            Z_5 = types.InlineKeyboardButton('Другие животные', callback_data='cvb')
            Z_6 = types.InlineKeyboardButton('Товары для животных', callback_data='nmq')

            Z_markup.add(Z_1, Z_2, Z_3, Z_4, Z_5, Z_6)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=Z_markup)

        elif call.data == 'DX':
            DX_markup = types.InlineKeyboardMarkup()
            DX_1 = types.InlineKeyboardButton('Готовый бизнес', callback_data='wert')
            DX_2 = types.InlineKeyboardButton('Оборудование для бизнеса', callback_data='yuio')

            DX_markup.add(DX_1, DX_2)

            bot.send_message(call.message.chat.id, 'Выберете подкатегорию', reply_markup=DX_markup)

        elif call.data == 'q' or call.data == 'w' or call.data == 'e' or call.data == 'r' or call.data == 't' \
                or call.data == 'y' or call.data == 'u' or call.data == 'i' or call.data == 'o' \
                or call.data == 'p' or call.data == 'a' or call.data == 's' or call.data == 'd' \
                or call.data == 'f' or call.data == 'g' or call.data == 'h' or call.data == 'j' \
                or call.data == 'k' or call.data == 'l' or call.data == 'z' or call.data == 'x' \
                or call.data == 'c' or call.data == 'v' or call.data == 'b' or call.data == 'n' \
                or call.data == 'm' or call.data == 'qw' or call.data == 'er' or call.data == 'ty' \
                or call.data == 'ui' or call.data == 'op' or call.data == 'as' or call.data == 'df' \
                or call.data == 'gh' or call.data == 'jk' or call.data == 'lz' or call.data == 'xc' \
                or call.data == 'vb' or call.data == 'nm' or call.data == 'qwe' or call.data == 'rty' \
                or call.data == 'uio' or call.data == 'pas' or call.data == 'dfg' or call.data == 'hjk' \
                or call.data == 'lzx' or call.data == 'cvb' or call.data == 'nmq' or call.data == 'wert' \
                or call.data == 'yuio':

            # получение текста , нажатой кнопки пользователем
            for i in call.message.json['reply_markup']['inline_keyboard']:
                for j in i:
                    if j['callback_data'] == call.data:
                        CATEGORY.append(j['text'])

            bot.send_message(call.message.chat.id,
                             'Ведите город в котором надо найти объявления ',
                             parse_mode='html')


# Непрерывная работа бота
bot.polling(none_stop=True)