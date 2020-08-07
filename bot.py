import requests
from time import sleep
import random

nouns = ("puppy", "car", "rabbit", "girl", "monkey")
verbs = ("runs", "hits", "jumps", "drives", "barfs") 
adv = ("crazily.", "dutifully.", "foolishly.", "merrily.", "occasionally.")
adj = ("adorable", "clueless", "dirty", "odd", "stupid")
l = [nouns,verbs,adj,adv]
def random_simple_sentence():
    return (' '.join([random.choice(i) for i in l])).capitalize()

class Bot():
    def send_message(self, chat, text):
        raise NotImplementedError

class TelegramBot(Bot):
    def __init__ (self, token):
        self.token = token
        self.url = "https://api.telegram.org/bot{}/".format(self.token)
    
    def get_updates_json(self, request):  
        response = requests.get(request + 'getUpdates')
        return response.json()

    def last_update(self, data):  
        results = data['result']
        total_updates = len(results) - 1
        for message in results:
            print(message)
        print('\n\n')
        return results[total_updates]

    def get_chat_id(self, update):  
        chat_id = update['message']['chat']['id']
        return chat_id

    def send_message(self, chat, text):  
        params = {'chat_id': chat, 'text': text}
        response = requests.post(self.url + 'sendMessage', data=params)
        return response

def main():
    t_bot = TelegramBot("1180087406:AAGv9j6GOyRdVvR1WnKXNn6Z8Z019wVqx2E")
    update_id = t_bot.last_update(t_bot.get_updates_json(t_bot.url))['update_id']
    while True:
        if update_id == t_bot.last_update(t_bot.get_updates_json(t_bot.url))['update_id']:
            last_chat_id = t_bot.get_chat_id(t_bot.last_update(t_bot.get_updates_json(t_bot.url)))
            t_bot.send_message(last_chat_id, random_simple_sentence())
            update_id += 1
        sleep(1)       

if __name__ == '__main__':  
    main()