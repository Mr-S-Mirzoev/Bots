import csv
import os
from security.token import UserToken
from copy import deepcopy
from datetime import datetime
import pandas

class RateWorker:
    class __RW:
        def load_categories(self):
            with open("./metainfo/categories.txt", 'r') as f:
                self.categories = set(x.strip() for x in f.readlines())
        
        def prepare(self, chat_id):
            #here chat_id is interpreted as user_id (may be wrong)
            chat_secure_id = UserToken(chat_id).get_token()
            if not os.path.isdir('./user-data'):
                os.mkdir('./user-data')
            if not os.path.isdir('./user-data/{}'.format(chat_secure_id)):
                os.mkdir('./user-data/{}'.format(chat_secure_id))
            if not os.path.isdir('./user-data/{}/ml-data'.format(chat_secure_id)):
                os.mkdir('./user-data/{}/ml-data'.format(chat_secure_id))
            if not os.path.isfile('./user-data/{}/ml-data/ratings.csv'.format(chat_secure_id)):
                with open('./user-data/{}/ml-data/ratings.csv'.format(chat_secure_id), mode='w') as csv_file:
                    fieldnames = ['title', 'link', 'tags', 'description', 'timestamp', 'rating']
                    writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                    writer.writeheader()

        def prepare_row(self, dct: dict, fieldnames: list):
            newdict = dict()
            for field in fieldnames:
                if field in dct.keys():
                    newdict[field] = dct[field]
                else:
                    newdict[field] = None
            return newdict

        def append(self, chat_id, info):
            self.prepare(chat_id)
            fieldnames = ['title', 'link', 'tags', 'description', 'timestamp', 'rating']

            cpy = self.prepare_row(info, fieldnames)
            cpy['timestamp'] = datetime.now().timestamp() #float 
            # back to human-readable dt_object = datetime.fromtimestamp(timestamp)

            chat_secure_id = UserToken(chat_id).get_token()
            with open('./user-data/{}/ml-data/ratings.csv'.format(chat_secure_id), mode='a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writerow(cpy)

            fieldnames_ui = ["timestamp", "eventType", "contentId", "personId"]
            ui_info = dict()
            ui_info['timestamp'] = cpy['timestamp']
            ui_info['eventType'] = cpy['rating']
            ui_info['contentId'] = info['contentId']
            ui_info['personId'] = chat_secure_id
            with open('./metainfo/user_interactions.csv', 'a') as csv_file:
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames_ui)
                writer.writerow(ui_info)

        def get_my_ratings(self, chat_id):
            chat_secure_id = UserToken(chat_id).get_token()
            df = pandas.read_csv('./user-data/{}/ml-data/ratings.csv'.format(chat_secure_id))
            df['timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
            print(df)

    instance = None
    def __init__ (self):
        if not RateWorker.instance:
            print("RW: Not yet created, creating")
            RateWorker.instance = RateWorker.__RW()
        else:
            print("RW: Already created, using previous")

    def append(self, chat_id, info):
        RateWorker.instance.append(chat_id, info)

    def get_my_ratings(self, chat_id):
        RateWorker.instance.get_my_ratings(chat_id)
