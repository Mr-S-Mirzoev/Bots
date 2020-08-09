import requests
from time import sleep
import random
import json
import porn_worker
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

    def get_all_recent_text(self, updates):
        chats = self.divide_by_chat_id(updates)
        texts = dict()
        for chat_id, chat in chats.items():
            s = str()
            for message in chat:
                try:
                    text = message["message"]["text"]
                    if text.strip() == "/selectpreferences":
                        if chat_id in self.flag.keys():
                            self.flag[chat_id][0] = True
                        else:
                            self.flag[chat_id] = [True, False]
                    elif text.strip() == "/choosedatabases":
                        if chat_id in self.flag.keys():
                            self.flag[chat_id][1] = True
                        else:
                            self.flag[chat_id] = [False, True]
                    else:
                        s += text + '\n'
                except:
                    pass
            texts[chat_id] = s
            #self.work_buttons(chat_id, chat)
        return texts
    """
    def work_buttons(self, chat_id, text):
        try:
            cur_flag = self.flag[chat_id]
            if cur_flag:
                self.awaiting_reply_flag[chat_id] = [False, False]
                if cur_flag[0]:
                    self.send_message("Choose up to five categories each in new line.", chat_id)
                    self.awaiting_reply_flag[chat_id][0] = True
                if cur_flag[1]:
                    self.pornsites = ["xnxx.com", "porn.com", "its.porn", "xvideos.com"]
                    databases = str()
                    for index, pornsite in enumerate(self.pornsites):
                        databases += '\n{}. {}'.format(index + 1, pornsite)
                    #databases = '\n1. xnxx.com\n2. porn.com\n3. its.porn\n4. xvideos.com'
                    msg_text = "Choose up to five databases by their number, separating them by \',\'.{}".format(databases)
                    self.send_message(msg_text, chat_id)
                    self.awaiting_reply_flag[chat_id][1] = True
                self.flag[chat_id] = (False, False)
            cur_flag = self.awaiting_reply_flag[chat_id]
            if cur_flag:
                pw = porn_worker.PornWorker()
                if cur_flag[0]:
                    numbers = set()
                    for str_val in text:
                        try:
                            num = int(str_val)
                            if num <= len(self.pornsites) and num >= 0:
                                numbers.add(num)
                        except ValueError:
                            categs = str_val.split('\n')
                            for category in categs:
                                if pw.check_if_is_category(category):
                                    if not self.user_preferences[chat_id]:
                                        self.user_preferences[chat_id] = list()
                                    self.user_preferences[chat_id].append(category)
                            
                if cur_flag[1]:
                    databases = '\n1. xnxx.com\n2. porn.com\n3. its.porn\n4. xvideos.com'
                    msg_text = "Choose up to five databases by their number, separating them by \',\'.{}".format(databases)
                    self.send_message(msg_text, chat_id)
                self.awaiting_reply_flag[chat_id] = (False, False)
        except KeyError:
            pass
        """

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