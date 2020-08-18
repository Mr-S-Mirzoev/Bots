import requests
from time import sleep
import random
import json
import porn_worker
import audio_worker
import os
import urllib
#from datetime import datetime
from security.token import UserToken

nouns = ("puppy", "car", "rabbit", "girl", "monkey")
verbs = ("runs", "hits", "jumps", "drives", "barfs") 
adv = ("crazily.", "dutifully.", "foolishly.", "merrily.", "occasionally.")
adj = ("adorable", "clueless", "dirty", "odd", "stupid")
l = [nouns,verbs,adj,adv]

def random_simple_sentence():
    return (' '.join([random.choice(i) for i in l])).capitalize()

class Bot():
    def send_message(self, text, chat_id):
        raise NotImplementedError

class TelegramBot(Bot):
    def __init__ (self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot{}/".format(self.token)
        self.nmessages = 0
        self.flag = dict()
        self.awaiting_reply_flag = dict()
        self.user_preferences = dict()
        self.porn_worker = porn_worker.PornWorker()
        self.audio_worker = audio_worker.AudioWorker()

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def get_updates(self, offset=None):
        url = self.url + "getUpdates"
        if offset:
            url += "?offset={}".format(offset)
        js = self.get_json_from_url(url)
        return js

    def get_last_update_id(self, updates):
        update_ids = []
        for update in updates["result"]:
            update_ids.append(int(update["update_id"]))
        return max(update_ids)

    def get_last_chat_id_and_text(self, updates):
        num_updates = len(updates["result"])
        last_update = num_updates - 1
        text = updates["result"][last_update]["message"]["text"]
        chat_id = updates["result"][last_update]["message"]["chat"]["id"]
        return (text, chat_id)

    def divide_by_chat_id(self, updates):
        chats = dict()
        for update in updates["result"]:
            chat_id = update["message"]["chat"]["id"]
            if chat_id not in chats.keys():
                chats[chat_id] = list()
            chats[chat_id].append(update)
        return chats

    def download_audio_file(self, chat_id, file_id):
        js = self.get_json_from_url("https://api.telegram.org/bot{}/getFile?file_id={}".format(self.token, file_id))
        file_path = js["result"]["file_path"]
        source = os.path.join('./files/{}'.format(chat_id), file_path)
        urllib.request.urlretrieve("https://api.telegram.org/file/bot{}/{}".format(self.token, file_path), source)
        return source

    def parse_and_lookup(self, text):
        words = text.split()
        options = list()
        for phrase in words:
            #print(phrase)
            if self.porn_worker.check_if_is_category(phrase):
                options.append(phrase)
        for i in range(len(words) - 1):
            phrase = words[i].lower() + ' ' + words[i + 1].lower()
            #print(phrase)
            if self.porn_worker.check_if_is_category(phrase):
                options.append(phrase)
        for i in range(len(words) - 2):
            phrase = words[i].lower() + ' ' + words[i + 1].lower() + ' ' + words[i + 2].lower()
            #print(phrase)
            if self.porn_worker.check_if_is_category(phrase):
                options.append(phrase)
        return options

    def get_all_recent_text(self, updates):
        chats = self.divide_by_chat_id(updates)
        texts = dict()
        for chat_id, chat in chats.items():
            s = str()
            for message in chat:
                try:
                    #left here
                    try:
                        text = message["message"]["text"]
                    except KeyError:
                        self.audio_worker.prepare_dir(chat_id)
                        file_id = message["message"]["voice"]["file_id"]
                        ogg_file_path = self.download_audio_file(chat_id, file_id)
                        mp3_file_path = self.audio_worker.ogg_to_mp3(ogg_file_path)
                        text = self.audio_worker.get_text(mp3_file_path)
                    s += text + '\n'
                except Exception as e:
                    print(e)
            texts[chat_id] = s
        return texts

    def reply_to_all(self, updates):
        text_updates = self.get_all_recent_text(updates)
        for update in updates["result"]:
            uid = update["message"]["from"]["id"]
            ut = UserToken(uid)
            token = ut.get_token()
            print(uid, token)
        for chat_id, text in text_updates.items():
            try:
                self.send_message(text, chat_id)
                self.download_audio_file()
            except Exception as e:
                print("Exception: {}".format(e))

    def send_message(self, text, chat_id):
        url = self.url + "sendMessage?text={}&chat_id={}".format(text, chat_id)
        self.get_url(url)

def TelegramBotWorker():
    with open("../t_bot_token.txt","r") as f:
        t_bot_token = f.readline().strip()
    t_bot = TelegramBot(t_bot_token)
    last_update_id = None
    while True:
        updates = t_bot.get_updates(last_update_id)
        if len(updates["result"]) > 0:
            last_update_id = t_bot.get_last_update_id(updates) + 1
            t_bot.reply_to_all(updates)
        sleep(0.5)

def main():
    TelegramBotWorker()

if __name__ == '__main__':  
    main()