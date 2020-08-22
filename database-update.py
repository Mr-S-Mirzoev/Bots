import requests, csv
from bs4 import BeautifulSoup
from abc import ABC, abstractmethod
from parse import parse
from random import choice
from copy import deepcopy
from datetime import datetime

databases = ['https://www.its.porn/', 'https://www.xnxx.com/']

class Database:
    def __init__(self, link):
        self.link = link

    @abstractmethod
    def get_lates_videos(self):
        pass

class ItsPorn(Database):
    def get_latest_videos(self):
        url = self.link
        response = requests.get(url)

        soup = BeautifulSoup(response.text, 'html.parser')
        all_links = soup.find_all("div", "item thumb")
        new_videos = list()
        for video in all_links:
            html_part = str(video.a)
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
            info['timestamp'] = datetime.now().timestamp() #float 
            # back to human-readable dt_object = datetime.fromtimestamp(timestamp)
            new_videos.append(info)
        return new_videos

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
                reply['tags'] = str(tags[0]).lower()
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

its_db = get_database_by_name('https://www.its.porn/')
lst = its_db.get_latest_videos()
#print(lst)
#print(len(lst))

with open("./metainfo/last-cid.txt", 'r') as c_file:
    clst = c_file.readlines()
    last_cid = int(clst[0])
    last_update = float(clst[1])
    print('Last ContentId = {}'.format(last_cid))
    print('Last update on {}'.format(datetime.fromtimestamp(last_update)))
with open("./metainfo/last-cid.txt", 'w') as c_file:
    c_file.write(str(last_cid + len(lst)) + '\n')
    c_file.write(str(datetime.now().timestamp()))

with open('./metainfo/shared_videos.csv', 'a') as wr_file:
    fieldnames = ['timestamp', 'contentId', 'link', 'title', 'text', 'tags']
    writer = csv.DictWriter(wr_file, fieldnames=fieldnames)
    print(lst, end='\n\n\n\n')
    print(lst[0])
    for num, value in enumerate(lst):
        info = dict()
        print(value, num)
        for field in fieldnames:
            try:
                if type(value[field]) == str:
                    info[field] = '"' + value[field] + '"'
                else:
                    info[field] = value[field]
            except KeyError:
                info['contentId'] = last_cid + num + 1
        writer.writerow(info)
