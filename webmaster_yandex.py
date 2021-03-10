#!/usr/bin/python3.8
import requests
import json
from config import *
import datetime
from dateutil import parser


class YaWebmaster:
    user_id = None

    def __init__(self):
        r = requests.get(url_userid, headers=headers)
        self.user_id = json.loads(r.text)['user_id']

    """
    get_hosts:
    Получаем словарь со списком доменов для user_id
    """

    def get_hosts(self):
        url = url_userid + str(self.user_id) + "/hosts"
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_col_history_in_search(self, host_id):
        date = datetime.datetime.utcnow().date()
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/search-urls/in-search/history?date_to=" + str(date)
        print(url)
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_ix_parameter(self, host_id):
        date = datetime.datetime.utcnow().date()
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/sqi-history?date_to=" + str(date)
        print(url)
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_diagnostics(self, host_id):
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/diagnostics"
        print(url)
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_summary(self, host_id):
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/summary"
        print(url)
        r = json.loads(requests.get(url, headers=headers).text)
        return r


def main():
    """
    Получаем количество URL в индексе за дату
    :return:
    """
    object_ya_webmaster = YaWebmaster()
    col_history_in_search = (object_ya_webmaster.get_col_history_in_search(host_id))
    for i in col_history_in_search['history']:
        date_webmaster = parser.parse(i['date'])  # дата в вебмастере
        num_urls_index = i['value']  # количество url в индексе за дату
        print(f"{date_webmaster.date()} - {num_urls_index}")
    """
    Получаем историю X параметра
    """
    ix = object_ya_webmaster.get_ix_parameter(host_id)
    for i in ix['points']:
        date_webmaster = parser.parse(i['date'])  # дата в вебмастере
        num_urls_index = i['value']  # величина Х за дату
        print(f"{date_webmaster.date()} - {num_urls_index}")
    """
    Проверка наличия ошибок и их даты возникновения
    """
    diagnos = object_ya_webmaster.get_diagnostics(host_id)
    for i in diagnos['problems']:
        """
        Название ошибка - Категория ошибки - Присутствует/Отсутствует - Дата ошибки
        """
        print(
            f"{i} - {diagnos['problems'][i]['severity']} - {diagnos['problems'][i]['state']} - {diagnos['problems'][i]['last_state_update']}")
    """
    Общая информация об индексировании сайта
    """
    summary = object_ya_webmaster.get_summary(host_id)
    ix = summary['sqi']  # икс
    excluded_pages = summary['excluded_pages_count']  # количество исключенных страниц из поиска на момент запроса
    searchable_pages = summary['searchable_pages_count']  # количество страниц в поиске на момент запроса
    print(f"{ix} - {excluded_pages} - {searchable_pages}")


if __name__ == 'main':
    main()
