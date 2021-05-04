#!/usr/bin/python3.8
import requests
import json
from config import *
import datetime
from dateutil import parser
from apache_mysql import MySQLi


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
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_ix_parameter(self, host_id):
        date = datetime.datetime.utcnow().date()
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/sqi-history?date_to=" + str(date)
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_diagnostics(self, host_id):
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/diagnostics"
        r = json.loads(requests.get(url, headers=headers).text)
        return r

    def get_summary(self, host_id):
        url = url_userid + str(self.user_id) + "/hosts/" + str(host_id) + \
              "/summary"
        r = json.loads(requests.get(url, headers=headers).text)
        return r


def check_success_domain(dictionary_domain):
    print(f"DICTIONARY_DOMAIN: {dictionary_domain}")
    try:
        print(dictionary_domain['error_message'])
        return dictionary_domain['error_message']
    except TypeError:
        return "OK"
    except KeyError:
        return "OK"

def main():
    """
    Получаем количество URL в индексе за дату
    :return:
    """
    object_ya_webmaster = YaWebmaster()
    hosts = object_ya_webmaster.get_hosts()
    db = MySQLi(host, user, password, database_home)
    for host_id in hosts['hosts']:
        if ':443' in host_id['host_id']:
            host_id = host_id['host_id']  # получаем в цикле сайт из списка
            error_message = check_success_domain(object_ya_webmaster.get_col_history_in_search(host_id))
            if error_message == "OK":
                check_string_in_db = db.fetch("SELECT * FROM a_team_webmaster_domains WHERE domain= %s", host_id)

                if not check_string_in_db['rows']:
                    db.commit("INSERT INTO a_team_webmaster_domains (domain) VALUES (%s)", host_id)
                col_history_in_search = (object_ya_webmaster.get_col_history_in_search(host_id))
                domain = db.fetch("SELECT id FROM a_team_webmaster_domains WHERE domain= %s", host_id)
                domain_id = domain['rows'][0][0]
                for i in col_history_in_search['history']:
                    date_webmaster = parser.parse(i['date']).date()  # дата в вебмастере
                    num_urls_index = i['value']  # количество url в индексе за дату
                    #
                    check_string_in_db = db.fetch("SELECT * FROM a_team_webmaster_index_date WHERE id_domain= %s"
                                                  " AND date= %s",
                                                  domain_id, date_webmaster)
                    if not check_string_in_db['rows']:
                        db.commit("INSERT INTO a_team_webmaster_index_date (id_domain, date, num_urls_in_index) "
                                  "VALUES (%s, %s, %s)", domain_id, date_webmaster, num_urls_index)

                """
                Получаем историю X параметра
                """
                ix = object_ya_webmaster.get_ix_parameter(host_id)
                for i in ix['points']:
                    date_webmaster = parser.parse(i['date'])  # дата в вебмастере
                    value_x = i['value']  # величина Х за дату

                    check_string_in_db = db.fetch("SELECT * FROM a_team_webmaster_parameter_x_date WHERE id_domain= %s"
                                                  " AND date= %s AND x_value = %s",
                                                  domain_id, date_webmaster, value_x)
                    if not check_string_in_db['rows']:
                        db.commit("INSERT INTO a_team_webmaster_parameter_x_date (id_domain, date, x_value) "
                                  "VALUES (%s, %s, %s)", domain_id, date_webmaster, value_x)

                """
                Проверка наличия ошибок и их даты возникновения
                """
                diagnos = object_ya_webmaster.get_diagnostics(host_id)
                date_check = datetime.datetime.utcnow().date()
                for i in diagnos['problems']:
                    """
                    Название ошибка - Категория ошибки - Присутствует/Отсутствует - Дата ошибки
                    """
                    error_name = i
                    category_error = diagnos['problems'][i]['severity']
                    status = diagnos['problems'][i]['state']
                    date_update = diagnos['problems'][i]['last_state_update']

                    check_string_in_db = db.fetch("SELECT * FROM a_team_webmaster_errors WHERE id_domain= %s"
                                                  " AND date_check= %s AND error_name = %s",
                                                  domain_id, date_check, error_name)
                    if not check_string_in_db['rows']:
                        db.commit(
                            "INSERT INTO a_team_webmaster_errors (id_domain, date_check, error_name, category_error,"
                            " status, date_update) "
                            "VALUES (%s, %s, %s, %s, %s, %s)", domain_id, date_check, error_name,
                            category_error, status, date_update)
                """
                Общая информация об индексации сайта
                """
                summary = object_ya_webmaster.get_summary(host_id)
                ix = summary['sqi']  # икс
                excluded_pages = summary['excluded_pages_count']  # количество исключенных страниц
                searchable_pages = summary['searchable_pages_count']  # количество страниц в поиске на момент запроса

                check_string_in_db = db.fetch("SELECT * FROM a_team_webmaster_summary WHERE id_domain= %s"
                                              " AND date_check= %s",
                                              domain_id, date_check)
                if not check_string_in_db['rows']:
                    db.commit("INSERT INTO a_team_webmaster_summary (id_domain, date_check, parameter_x, excluded_pages,"
                              " searchable_pages) "
                              "VALUES (%s, %s, %s, %s, %s)", domain_id, date_check, ix, excluded_pages, searchable_pages)


# if __name__ == 'main':
main()
