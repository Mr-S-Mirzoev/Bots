import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from parse import parse
from random import choice
from copy import deepcopy

databases = ['https://www.its.porn/', 'https://www.xnxx.com/']

class Database:
    def __init__(self, link):
        self.link = link

    @abstractmethod
    def get_random_video(self):
        pass

class ItsPorn(Database):
    def get_random_video(self):
        url = self.link
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all("div", "item thumb")
        random_video = choice(all_links)
        html_part = str(random_video.a)
        result = parse("<a{}href={} title={}>{}data-original={} height={}</a>", html_part)
        info = dict()
        info["link"] = result[1][1:-1]
        info["image"] = result[4][1:-1]

        reply = self.get_tags_and_description(info['link'])
        info["description"] = deepcopy(reply['description'])
        info['tags'] = deepcopy(reply['tags'])

        #print(info)

        title = result[2][1:-1]
        index = len(title)
        while title[index - 1].isnumeric():
            index -= 1
        info["title"] = title[:index]
        return info

    def get_tags_and_description(self, link):
        url = link
        response = requests.get(url)
        reply = dict()
        reply['tags'] = None
        reply['description'] = None

        soup = BeautifulSoup(response.text, 'html.parser')
        for value in soup.find_all("meta"):
            if not reply['tags'] and str(value).find('name="keywords"') > 0:
                tags = parse('<meta content="{}" name="keywords"/>', str(value))
                reply['tags'] = tags[0]
            if not reply['description'] and str(value).find('property="og:description"') > 0:
                txt = str(value)[str(value).rfind('<meta content'):]
                tags = parse('<meta content="{}" property="og:description">{}</meta>', txt)
                reply['description'] = tags[0]
            if reply['tags'] and reply['description']:
                break
        
        return reply

def get_database_by_name(name):
    if name == 'https://www.its.porn/':
        return ItsPorn('https://www.its.porn/')
    elif name == 'https://www.xnxx.com/':
        return Database('https://www.xnxx.com/')
    else:
        raise NameError

class PornWorker:
    def __init__ (self):
        self.categories = None
    
    def check_if_valid_url (self, message):
        try:
            requests.get("http://www.avalidurl.com/")
            print("URL is valid and exists on the internet")
        except requests.ConnectionError:
            print("URL does not exist on Internet")

    def load_categories (self):
        with open("./metainfo/categories.txt", 'r') as f:
            self.categories = set(x.strip() for x in f.readlines())
    
    def check_if_is_category(self, value):
        if not self.categories:
            self.load_categories()
        return value.strip() in self.categories

    def check_if_has_categories(self, text: str):
        lst = [x.lower() for x in text.split()]
        cats = list()
        length = len(lst)
        for i in range(length):
            if self.check_if_is_category(lst[i]):
                cats.append(lst[i])
        for wordcount in range(2, 4 + 1):
            for i in range(length - wordcount + 1):
                val = ' '.join(lst[i : i + wordcount])
                if self.check_if_is_category(val):
                    cats.append(val)
        return cats

#itsp = ItsPorn(databases[0])
#print(itsp.get_random_video())