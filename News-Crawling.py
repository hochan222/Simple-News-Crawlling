# Libraries
# BeautifulSoup4, lxml, requests
# pip install python-dateutil

# 크롤링하기전에 MainDomain/robots.txt 로 허가권 확인하기.
# BeautifulSoup ==> find_all(name, attrs, recursive, string, limit, **kwargs)
#                   find(name, attrs, recursive, string, **kwargs)

import re
import string
import requests
import datetime
from bs4 import BeautifulSoup
from dateutil.parser import parse
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

def get_list_article_headline(url):
    article_head = dict()
    page = 1

    # dt is 7days before
    p_date = re.compile('\d+-\d+-\d+')
    dt = datetime.datetime.now() - datetime.timedelta(days=7)

    while True:
        url_mix = '{0}{1}.html'.format(url, page)
        print('Collecting Page from URL : ' + url_mix)
        source = requests.get(url_mix).text
        soup = BeautifulSoup(source, 'lxml')
        article = soup.find_all('div', class_='list_article_area')

        for i in range(len(article)):
            try:
                head = article[i].find('div', class_='list_article_headline HD').text
                date = p_date.findall(article[i].find('div', class_='list_article_byline2').text)[0]
            except Exception as e:
                print(e)
            if parse(date).date() > dt.date():
                article_head[head] = date
            else:
                return article_head
        page += 1


def refine_word(text):
    tokens = word_tokenize(text)
    tokens = [w.lower() for w in tokens]
    table = str.maketrans('', '', string.punctuation)
    stripped = [w.translate(table) for w in tokens]
    words = [word for word in stripped if word.isalpha()]
    stop_words = set(stopwords.words('english'))
    words = [w for w in words if not w in stop_words]

    return words


if __name__ == '__main__':
    korea_times_url = 'http://www.koreatimes.co.kr/www2/index.asp'
    url_list = {
        "korea_times_economy": 'http://www.koreatimes.co.kr/www/sublist_602_',
        "korea_times_entertainment": 'http://www.koreatimes.co.kr/www/sublist_398_',
        "korea_times_biz_tech": 'http://www.koreatimes.co.kr/www/sublist_129_',
        "korea_times_sports": 'http://www.koreatimes.co.kr/www/sublist_600_',
        "korea_times_world": 'http://www.koreatimes.co.kr/www/sublist_501_'
    }

    result = {}
    words_dict = {}

    for i in url_list.values():
        result = {**result, **get_list_article_headline(i)}

    result_text = ''.join(list(result.keys()))
    words = refine_word(result_text)

    for word in words:
        if word not in words_dict:
            words_dict[word] = 1
        else:
            words_dict[word] += 1

    words_dict = sorted(words_dict.items(), key=lambda x: x[1], reverse=True)[:10]

    print(words_dict)
