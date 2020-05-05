import requests
from config import *
import bs4
import csv


class Avito_parser_main(object):
    '''
    класс отвечающий за парсинг авито с параметрами
    '''

    def __init__(self, categories: str, town: str, price_now: str = None, price_old: str = None, item: str = None):
        self.BASE_URL = BASE_URL
        self.url = requests.get(self.get_url(categories, town)).url
        self.item = item
        if self.item:
            self.url_get_pagination = requests.get(self.get_url(categories, town), params={'q': self.item}).text

        else:
            self.url_get_pagination = requests.get(self.get_url(categories, town)).text
        self.price_now = price_now
        self.price_old = price_old

        self.params = {}
        self.session = requests.Session()
        self.headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

    def get_url(self, category: str, town: str) -> str:
        '''
        Получаем url с городом и категорией
        :param category:
        :param town:
        :return:
        '''
        url_address = self.BASE_URL + str(self.Towner_and_Item(town) + '/' + str(self.Towner_and_Item(category)))
        print(url_address)
        return url_address

    def get_pagination(self, text: str):
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

    def parametring(self, page: int, item: str = None) -> requests.models.Response:
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

    def parsing_block(self, result: requests.models.Response) -> list:
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
                        price = price

                    else:
                        price = ''

                elif self.price_now:
                    pri_ce = self.number(price[:-5])
                    if int(self.price_now) <= int(pri_ce):
                        price = price

                    else:
                        price = ''

                elif self.price_old:
                    pri_ce = self.number(price[:-5])
                    if int(pri_ce) <= int(self.price_old):
                        price = el.select_one('span.snippet-price').text.strip().replace('₽', 'руб')

                    else:
                        price = ''

                else:
                    price = price

            except:
                name_class = self.__class__
                name_cls = str(name_class)[17:-2]
                name_cls_child = str(name_class)[21:-2]
                if name_cls == 'Avito_parser_main' or name_cls_child == 'Avito_href':
                    try:
                        price = price

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

    def csv_writer(self, data: list):
        '''
        Запись словаря data из parsing_block в csv
        :param data:
        :return:
        '''
        with open('text.xlsx', 'a') as f:
            writer = csv.writer(f)
            for i in data:
                writer.writerow((i[0],
                                 i[1],
                                 i[2],
                                 i[3]))

    def Towner_and_Item(self, Town: str) -> str:
        '''
        Перевод русской речи на английскую , для того чтобы можно было задать параметры для ссылки
        :param Town:
        :return:
        '''
        result = Town.lower()
        res = ''
        for i in result:
            try:
                res += dict_ru_en[i]

            except:
                return result

        return res

    def number(self, numb: str) -> str:
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

    def __init__(self, href: str):
        super(Avito_parser_main, self).__init__()
        self.href = href
        self.params = {}
        self.text_href = requests.get(self.href).text
        self.session = requests.Session()
        self.headers = {
            'accept': '*/*',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.130 Safari/537.36'
        }

    def parametr(self, page: int):
        if page >= 1:
            self.params['p'] = page
            result = self.session.get(url=self.href, params=self.params)

        else:
            result = self.session.get(url=self.href)

        return result
