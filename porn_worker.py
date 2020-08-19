import requests
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from parse import parse
from random import choice

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
        videos = list()
        for links in soup.find_all("div", "item thumb"):
            html_part = str(links.a)
            result = parse("<a{}href={} title={}>{}data-original={} height={}</a>", html_part)
            info = dict()
            info["link"] = result[1][1:-1]
            info["image"] = result[4][1:-1]

            title = result[2][1:-1]
            index = len(title)
            while title[index - 1].isnumeric():
                index -= 1
            info["title"] = title[:index]
            videos.append(info)
            #print(info, end='\n\n\n')
        
        return choice(videos)

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
