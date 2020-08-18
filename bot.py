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
from message import Message
from state_table import StateTable

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
        self.statetable = StateTable()

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

    def work_updates(self, updates):
        chats = self.divide_by_chat_id(updates)
        for chat_id, chat in chats.items():
            for message in chat:
                msg = Message(message["message"], chat_id, self.token, self.statetable)
                for reply in msg.reply():
                    self.send_message(reply, chat_id)

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
            t_bot.work_updates(updates)
        sleep(0.5)

def main():
    TelegramBotWorker()

if __name__ == '__main__':  
    main()