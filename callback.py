from state_table import State, StateTable
from abc import ABC, abstractmethod
from porn_worker import PornWorker, databases, get_database_by_name
from random import choice
import os, requests
from security.token import UserToken
from copy import deepcopy
from rating_worker import RateWorker

def prepare_user_dir(chat_id):
    #here chat_id is interpreted as user_id (may be wrong)
    chat_secure_id = UserToken(chat_id).get_token()
    if not os.path.isdir('./user-data'):
        os.mkdir('./user-data')
    if not os.path.isdir('./user-data/{}'.format(chat_secure_id)):
        os.mkdir('./user-data/{}'.format(chat_secure_id))

class Callback:
    @abstractmethod
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        if text.strip().lower() == 'exit':
            state_tbl.buffer[chat_id] = None
            state_tbl.states[chat_id] = State.NORMAL
            return "Alright, back into main menu"

class Command:
    def __init__(self, name: str, callback: Callback):
        self.name = name
        self.callback = callback

class CommandList:
    def __init__(self):
        self.command_list = dict() # enum_no - (command_name, callback)

    def register(self, name: str, enum_no: State, callback: Callback):
        self.command_list[enum_no] = Command(name, callback)
        print("Registred command {} which referes to State = {}".format(name, enum_no))
    
    def act(self, text, state_tbl: StateTable, chat_id):
        try:
            state = state_tbl.states[chat_id]
        except KeyError:
            state_tbl.states[chat_id] = State.NORMAL
            state = state_tbl.states[chat_id]
        try:
            return self.command_list[state].callback(text, state_tbl, chat_id)
        except Exception as e:
            result = dict()
            result["text"] = "LOGIC ERROR, no such State available or {}".format(e)
            return result

class NormalCallback(Callback):
    def prepare_dir(self, chat_id):
        #here chat_id is interpreted as user_id (may be wrong)
        chat_secure_id = UserToken(chat_id).get_token()
        if not os.path.isdir('./user-data'):
            os.mkdir('./user-data')
        if not os.path.isdir('./user-data/{}'.format(chat_secure_id)):
            os.mkdir('./user-data/{}'.format(chat_secure_id))
        if not os.path.isdir('./user-data/{}/photo'.format(chat_secure_id)):
            os.mkdir('./user-data/{}/photo'.format(chat_secure_id))

    def download_photo(self, chat_id, link: str):
        file_path = link[link.rfind('/') + 1:]

        #here chat_id is interpreted as user_id (may be wrong)
        chat_secure_id = UserToken(chat_id).get_token()
        source = os.path.join('./user-data/{}/photo'.format(chat_secure_id), file_path)
        response = requests.get(link)

        file = open(source, "wb")
        file.write(response.content)
        file.close()
        return source

    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        reply = str()
        photo = None
        if text == "/selectpreferences":
            state_tbl.states[chat_id] = State.WAITING_GET_CATEGORIES
            reply = "Type in categories or record them on voice message"
        elif text == "/choosedatabases":
            state_tbl.states[chat_id] = State.WAITING_SET_DBS
            state_tbl.buffer[chat_id] = databases
            reply = "Choose any of these dbs. In reply pass numbers separated with spaces ex.: '1 12 13':\n"
            for num, website in enumerate(databases):
                reply += str(num + 1) + ') ' + website + '\n'
        elif text == '/randomvideo':
            state_tbl.states[chat_id] = State.WAITING_FOR_RATING
            secure_chat_id = UserToken(chat_id).get_token()
            try:
                with open("./user-data/{}/prefered-databases.txt".format(secure_chat_id), 'r') as f:
                    user_db = list(x.strip() for x in f.readlines())
            except:
                user_db = ['https://www.its.porn/'] # default
            #user_db = ['https://www.its.porn/'] #TODO: change to get dbs from buffer
            db = get_database_by_name(choice(user_db))
            video = db.get_random_video()
            reply = video['title'] + '\n\nLink: ' + video['link'] + '\n\nReply with "like" or "dislike".'
            self.prepare_dir(chat_id)
            photo = self.download_photo(chat_id, video['image'])
            state_tbl.buffer[chat_id] = deepcopy(video)
        elif text == '/myinfo':
            secure_chat_id = UserToken(chat_id).get_token()
            print(chat_id, secure_chat_id)
            try:
                with open("./user-data/{}/prefered-categories.txt".format(secure_chat_id), 'r') as f:
                    lst = [x.strip() for x in f.readlines()]
                    if (len(lst) > 1):
                        reply += "Well, your preferences in categories are:\n"
                    else:
                        reply += "Well, your preference in categories is:\n"
                    for category in lst:
                        reply += category + '\n'
            except:
                reply += "No preferences in categories yet. Set them by /selectpreferences"

            secure_chat_id = UserToken(chat_id).get_token()
            try:
                with open("./user-data/{}/prefered-databases.txt".format(secure_chat_id), 'r') as f:
                    lst = [x.strip() for x in f.readlines()]
                    if (len(lst) > 1):
                        reply += "\nWell, your preferences in databases are:\n"
                    else:
                        reply += "\nWell, your preference in databases is:\n"
                    for category in lst:
                        reply += category + '\n'
            except:
                reply += "\nNo preferences in databases yet. Set them by /choosedatabases"
        else:
            reply += "I am not ready to talk, please choose commands:\n"
            reply += "/selectpreferences to set the prefered categories\n"
            reply += "/choosedatabases to choose websites you want to see porn from.\n"
            reply += "/randomvideo to get random video and rate it afterwards."
            reply += "/myinfo to get your information"
        result = dict()
        result["text"] = reply
        if photo:
            result['photo'] = photo
        return result

class RatingCallback(Callback):
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        super().__call__(text, state_tbl, chat_id)
        reply = str()
        state_tbl.states[chat_id] = State.NORMAL
        if text == 'like':
            state_tbl.buffer[chat_id]['rating'] = 'like'
            rw = RateWorker()
            rw.append(chat_id, state_tbl.buffer[chat_id])
            rw.get_my_ratings(chat_id)
            state_tbl.buffer[chat_id] = None
            reply = "We love to hear that you've liked our video!"
        elif text == 'dislike':
            state_tbl.buffer[chat_id]['rating'] = 'dislike'
            rw = RateWorker()
            rw.append(chat_id, state_tbl.buffer[chat_id])
            rw.get_my_ratings(chat_id)
            state_tbl.buffer[chat_id] = None
            reply = "Oh, that's a pity. We would do better next time!"
        else:
            reply = "Unknown reply. Try with 'like' or 'dislike'"
            state_tbl.states[chat_id] = State.WAITING_FOR_RATING
        result = dict()
        result["text"] = reply
        return result
        

class GetCategoriesCallback(Callback):
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        super().__call__(text, state_tbl, chat_id)
        reply = str()
        pw = PornWorker()
        state_tbl.buffer[chat_id] = pw.check_if_has_categories(text)
        if state_tbl.buffer[chat_id]:
            reply += "Choose categories. In reply pass numbers separated with spaces ex.: '1 12 13':\n"
            for num, cat in enumerate(state_tbl.buffer[chat_id]):
                reply += str(num + 1) + ') ' + cat + '\n'
            state_tbl.states[chat_id] = State.WAITING_SET_CATEGORIES
        else:
            reply += "Found no categories in \'{}\', try to type or record them again".format(text)
        result = dict()
        result["text"] = reply
        return result

class SetCategoriesCallback(Callback):
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        super().__call__(text, state_tbl, chat_id)
        lst = text.split()
        nums = list()
        reply = str()
        for word in lst:
            try:
                nums.append(int(word))
            except:
                continue
        if nums:
            buff = state_tbl.buffer[chat_id]
            lst = list()
            for number in nums:
                if number <= len(buff) and number >= 1:
                    lst.append(buff[number - 1])
            if lst:
                if (len(lst) > 1):
                    reply = "Added these categories to your preferences: " + ', '.join(lst)
                else:
                    reply = "Added this category to your preferences: " + lst[0]
                # assuming chat_id is user_id
                secure_chat_id = UserToken(chat_id).get_token()
                prepare_user_dir(chat_id)
                with open("./user-data/{}/prefered-categories.txt".format(secure_chat_id), 'w') as f:
                    for category in lst:
                        f.write(category + '\n')
                state_tbl.buffer[chat_id] = None
                state_tbl.states[chat_id] = State.NORMAL
            else:
                reply = "Passed wrong numbers"
        else:
            reply = "Passed numbers in wrong format or didn't pass them at all"
        result = dict()
        result["text"] = reply
        return result

class DatabaseCallback(Callback):
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        super().__call__(text, state_tbl, chat_id)
        lst = text.split()
        nums = list()
        reply = str()
        for word in lst:
            try:
                nums.append(int(word))
            except:
                continue
        if nums:
            buff = state_tbl.buffer[chat_id]
            lst = list()
            for number in nums:
                if number <= len(buff) and number >= 1:
                    lst.append(buff[number - 1])
            if lst:
                if (len(lst) > 1):
                    reply = "Added these databases to your preferences: " + ', '.join(lst)
                else:
                    reply = "Added this database to your preferences: " + lst[0]
                secure_chat_id = UserToken(chat_id).get_token()
                prepare_user_dir(chat_id)
                with open("./user-data/{}/prefered-databases.txt".format(secure_chat_id), 'w') as f:
                    for database in lst:
                        f.write(database + '\n')
                state_tbl.buffer[chat_id] = None
                state_tbl.states[chat_id] = State.NORMAL
            else:
                reply = "Passed wrong numbers"
        else:
            reply = "Passed numbers in wrong format or didn't pass them at all"
        result = dict()
        result["text"] = reply
        return result

class CallbackWorker:
    class __CW:
        def __init__(self):
            self.list = CommandList()
            self.register()

        def register(self):
            self.list.register('normal_action', State.NORMAL, NormalCallback())
            self.list.register('rating_action', State.WAITING_FOR_RATING, RatingCallback())
            self.list.register('get_categories_action', State.WAITING_GET_CATEGORIES, GetCategoriesCallback())
            self.list.register('set_categories_action', State.WAITING_SET_CATEGORIES, SetCategoriesCallback())
            self.list.register('set_databases_action', State.WAITING_SET_DBS, DatabaseCallback())

    instance = None
    def __init__ (self):
        if not CallbackWorker.instance:
            print("CW: Not yet created, creating")
            CallbackWorker.instance = CallbackWorker.__CW()
        else:
            print("CW: Already created, using previous")
        self.list = CallbackWorker.instance.list

    def act(self, text: str, state_tbl: StateTable, chat_id):
        return self.list.act(text, state_tbl, chat_id)