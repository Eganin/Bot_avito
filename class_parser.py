import requests
from config import *
import bs4
import csv


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
        with open('text.xlsx', 'a') as f:
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
