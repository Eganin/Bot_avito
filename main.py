import telebot
from telebot import types
from config import *
import os
import os.path
from class_parser import Avito_parser_main
from class_parser import Avito_href

CNT = 0
#  списки для хранения параметров
PRICE_NOW = []

PRICE_OLD = []

HREF = []

TOWN = []

ITEM = []

CATEGORY = []

bot = telebot.TeleBot(TG_TOKEN)


def main_main(town, category, item=None, price_now=None, price_old=None, messing=None):
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

    message = []
    cls = Avito_parser_main(category, town, price_now, price_old, item)
    r = cls.url_r
    rang = cls.get_pagination(r)
    for i in range(1, int(rang) + 1):
        if item:
            text = cls.parametring(page=i, item=item)

        else:
            text = cls.parametring(page=i)

        res = cls.parsing_block(text)
        if messing == 1:
            message.append(res)

        else:
            cls.csv_writer(res)

    if message:
        return message


def main_href(href, messing=None):
    '''
    Аналогичная функция запуска парсера без параметров
    :param href:    :param href:
    :return:
    '''
    message = []
    cls = Avito_href(href)
    r = cls.text_href
    rang = cls.get_pagination(r)
    for i in range(1, int(rang) + 1):
        text = cls.parametr(page=i)
        res = cls.parsing_block(text)
        if messing == 1:
            message.append(res)

        else:
            cls.csv_writer(res)

    return message


def return_callback():
    ITEM[:] = []

    PRICE_OLD[:] = []

    PRICE_NOW[:] = []

    CATEGORY[:] = []

    HREF[:] = []

    TOWN[:] = []


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
    board_3 = types.KeyboardButton('Сбросить все')

    markup.add(board_1, board_2, board_3)
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

        elif message.text.lower().strip() == 'сбросить все':
            bot.send_message(message.from_user.id, 'Настройки сброшены')

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
                                 'Введите максимальную цену продукта , если не надо ставьте прочерк')

            elif CNT == 3:
                price_old = message.text.lower().strip()
                if price_old == '-':
                    price_old = 1

                PRICE_OLD.append(price_old)
                CNT = 0

                bot.send_message(message.chat.id,
                                 'Нужные данные введены , парсинг может занять боллее 5 минут , пожалуйста имейте терпение')
                markup_variance = types.InlineKeyboardMarkup()
                mark_1 = types.InlineKeyboardButton('Отправить сообщением', callback_data='mess')
                mark_2 = types.InlineKeyboardButton('Отправить файлом xlsx', callback_data='xlsx')
                mark_3 = types.InlineKeyboardButton('Отправить файлом csv', callback_data='csv')
                markup_variance.add(mark_1, mark_2, mark_3)
                bot.send_message(message.chat.id, 'Выберете удобный вам способ отправки',
                                 reply_markup=markup_variance)


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

        elif call.data == 'mess' or call.data == 'mess_enclosing':
            def worker_message(enclosing):
                def data_reparing(dictionary):
                    mess_res = f"Название : {dictionary['title']}\n" \
                               f"Ссылка : {dictionary['href']}\n" \
                               f"Цена : {dictionary['price']}\n" \
                               f"Адресс : {dictionary['address']}\n"

                    return mess_res

                try:
                    if enclosing == 'mess':
                        main = main_main
                        result_message = main(town=TOWN[-1], category=CATEGORY[-1], item=ITEM[-1],
                                              price_now=PRICE_NOW[-1],
                                              price_old=PRICE_OLD[-1], messing=1)

                    elif enclosing == 'mess_enclosing':
                        main = main_href
                        result_message = main(href=HREF[-1], messing=1)

                    for i in result_message:
                        for j in i:
                            bot.send_message(call.message.chat.id, data_reparing(j))

                    bot.send_message(call.message.chat.id, 'Парсинг закончился')

                except Exception as e:
                    bot.send_message(call.message.chat.id, f'Произошла ошибка повторите еще раз пожалуйста {e}')

            worker_message(call.data)

        elif call.data == 'xlsx' or call.data == 'csv' or call.data == 'xlsx_enclosing' or call.data == 'csv_enclosing':
            def xlsx_and_csv(file_path, var_enc):
                if os.path.exists(file_path):
                    os.remove(file_path)
                    with open(file_path, 'w+') as file:
                        pass

                        def work_cmd(main):
                            with open(file_path, 'rb') as file:

                                try:
                                    if main == main_main:
                                        main_main(town=TOWN[-1], category=CATEGORY[-1], item=ITEM[-1],
                                                  price_now=PRICE_NOW[-1],
                                                  price_old=PRICE_OLD[-1])

                                    elif main == main_href:
                                        main_href(href=HREF[-1])

                                    bot.send_document(call.message.chat.id, file)

                                    return_callback()

                                except Exception as e:
                                    bot.send_message(call.message.chat.id,
                                                     f'Произошла ошибка повторите еще раз пожалуйста {e}')

                        if var_enc == 'not_enclosing':
                            work_cmd(main_main)

                        elif var_enc == 'enclosing':
                            work_cmd(main_href)

            if call.data == 'csv':
                xlsx_and_csv('text.csv', 'not_enclosing')

            elif call.data == 'xlsx':
                xlsx_and_csv('text.xlsx', 'not_enclosing')

            elif call.data == 'xlsx_enclosing':
                xlsx_and_csv('text.xlsx', 'enclosing')

            elif call.data == 'csv_enclosing':
                xlsx_and_csv('text.csv', 'enclosing')


        elif call.data == 'parsing':
            mark_enclosing_variance = types.InlineKeyboardMarkup()
            m_enclosing_1 = types.InlineKeyboardButton('Сообщением', callback_data='mess_enclosing')
            m_enclosing_2 = types.InlineKeyboardButton('Файлом csv', callback_data='csv_enclosing')
            m_enclosing_3 = types.InlineKeyboardButton('Файлом xlsx', callback_data='xlsx_enclosing')
            mark_enclosing_variance.add(m_enclosing_1, m_enclosing_2, m_enclosing_3)
            bot.send_message(call.message.chat.id, 'Выберите вариант отправки', reply_markup=mark_enclosing_variance)

        elif call.data == 'noup':
            return_callback()
            bot.send_message(call.message.chat.id, 'Парсинг отменен')

        elif call.data == 'OK':
            mark_start_href = types.InlineKeyboardMarkup()
            href_button = types.InlineKeyboardButton('Начать', callback_data='parsing')
            href_button_2 = types.InlineKeyboardButton('Отмена', callback_data='noup')
            mark_start_href.add(href_button, href_button_2)
            bot.send_message(call.message.chat.id, 'Выберите', reply_markup=mark_start_href)

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
if __name__ == '__main__':
    bot.polling(none_stop=True)
