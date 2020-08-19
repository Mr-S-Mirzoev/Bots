from state_table import State, StateTable
from abc import ABC, abstractmethod
from porn_worker import PornWorker, databases, get_database_by_name
from random import choice

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
        except:
            return "LOGIC ERROR, no such State available"

class NormalCallback(Callback):
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        reply = str()
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
            state_tbl.buffer[chat_id] = databases
            user_db = ['https://www.its.porn/'] #change to get dbs from buffer
            db = get_database_by_name(choice(user_db))
            video = db.get_random_video()
            reply = video['title'] + '\nLink: ' + video['link'] + '\n\nReply with "like" or "dislike".'
        else:
            reply += "I am not ready to talk, please choose commands:\n"
            reply += "/selectpreferences to set the prefered categories\n"
            reply += "/choosedatabases to choose websites you want to see porn from.\n"
            reply += "/randomvideo to get random video and rate it afterwards."
        return reply

class RatingCallback(Callback):
    def __call__(self, text: str, state_tbl: StateTable, chat_id):
        super().__call__(text, state_tbl, chat_id)
        reply = str()
        state_tbl.states[chat_id] = State.NORMAL
        if text == 'like':
            reply = "We love to hear that you've liked our video!"
        elif text == 'dislike':
            reply = "Oh, that's a pity. We would do better next time!"
        else:
            reply = "Unknown reply. Try with 'like' or 'dislike'"
            state_tbl.states[chat_id] = State.WAITING_FOR_RATING
        return reply
        

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
        return reply

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
                reply = "Added these categories to your preferences: " + ', '.join(lst)
                state_tbl.buffer[chat_id] = None
                state_tbl.states[chat_id] = State.NORMAL
            else:
                reply = "Passed wrong numbers"
        else:
            reply = "Passed numbers in wrong format or didn't pass them at all"
        return reply

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
                reply = "Added these categories to your preferences: " + ', '.join(lst)
                state_tbl.buffer[chat_id] = None
                state_tbl.states[chat_id] = State.NORMAL
            else:
                reply = "Passed wrong numbers"
        else:
            reply = "Passed numbers in wrong format or didn't pass them at all"
        return reply

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