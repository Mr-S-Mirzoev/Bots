from enum import Enum
from porn_worker import PornWorker, databases

class State(Enum):
    NORMAL = 1
    WAITING_FOR_RATING = 2
    WAITING_GET_CATEGORIES = 3
    WAITING_SET_CATEGORIES = 4
    WAITING_SET_DBS = 5

class StateTable:
    class __ST:
        def __init__(self):
            self.states = dict()
            self.buffer = dict()

        def update_state(self, chat_id, newstate, newbuf):
            self.states[chat_id] = newstate
            self.buffer[chat_id] = newbuf

    instance = None
    def __init__ (self):
        if not StateTable.instance:
            print("ST: Not yet created, creating")
            StateTable.instance = StateTable.__ST()
        else:
            print("ST: Already created, using previous")
        self.states = StateTable.instance.states
        self.buffer = StateTable.instance.buffer

    def update_state(self, chat_id, newstate, newbuf = None):
        StateTable.instance.update_state(chat_id, newstate, newbuf)

class Action:
    def __init__(self, state_tbl: StateTable, chat_id):
        self.chat_id = chat_id
        self.table = state_tbl

    def act(self, text):
        try:
            state = self.table.states[self.chat_id]
        except KeyError:
            self.table.states[self.chat_id] = State.NORMAL
            state = self.table.states[self.chat_id]
        if state == State.NORMAL:
            return self.act_normal(text)
        elif state == State.WAITING_FOR_RATING:
            return self.act_rating(text)
        elif state == State.WAITING_SET_CATEGORIES:
            return self.act_set_categories(text)
        elif state == State.WAITING_GET_CATEGORIES:
            return self.act_get_categories(text)
        elif state == State.WAITING_SET_DBS:
            return self.act_work_db(text)
        else:
            return "LOGIC ERROR, no such State available"

    def act_normal(self, text):
        reply = str()
        if text == "/selectpreferences":
            self.table.states[self.chat_id] = State.WAITING_GET_CATEGORIES
            reply = "Type in categories or record them on voice message"
        elif text == "/choosedatabases":
            self.table.states[self.chat_id] = State.WAITING_SET_DBS
            self.table.buffer[self.chat_id] = databases
            reply = "Choose any of these dbs. In reply pass numbers separated with spaces ex.: '1 12 13':\n"
            for num, website in enumerate(databases):
                reply += str(num + 1) + ') ' + website + '\n'
        else:
            reply += "I am not ready to talk, please choose commands:\n"
            reply += "/selectpreferences to set the prefered categories\n"
            reply += "/choosedatabases to choose websites you want to see porn from."
        return reply

    def act_rating(self, text):
        pass

    def act_get_categories(self, text: str):
        if text.strip().lower() == 'exit':
            self.table.buffer[self.chat_id] = None
            self.table.states[self.chat_id] = State.NORMAL
            return "Alright, back into main menu"
        reply = str()
        pw = PornWorker()
        self.table.buffer[self.chat_id] = pw.check_if_has_categories(text)
        if self.table.buffer[self.chat_id]:
            reply += "Choose categories. In reply pass numbers separated with spaces ex.: '1 12 13':\n"
            for num, cat in enumerate(self.table.buffer[self.chat_id]):
                reply += str(num + 1) + ') ' + cat + '\n'
            self.table.states[self.chat_id] = State.WAITING_SET_CATEGORIES
        else:
            reply += "Found no categories in \'{}\', try to type or record them again".format(text)
        return reply

    def act_set_categories(self, text: str):
        if text.strip().lower() == 'exit':
            self.table.buffer[self.chat_id] = None
            self.table.states[self.chat_id] = State.NORMAL
            return "Alright, back into main menu"
        lst = text.split()
        nums = list()
        reply = str()
        for word in lst:
            try:
                nums.append(int(word))
            except:
                continue
        if nums:
            buff = self.table.buffer[self.chat_id]
            lst = list()
            for number in nums:
                if number <= len(buff) and number >= 1:
                    lst.append(buff[number - 1])
            if lst:
                reply = "Added these categories to your preferences: " + ', '.join(lst)
                self.table.buffer[self.chat_id] = None
                self.table.states[self.chat_id] = State.NORMAL
            else:
                reply = "Passed wrong numbers"
        else:
            reply = "Passed numbers in wrong format or didn't pass them at all"
        return reply

    def act_work_db(self, text: str):
        if text.strip().lower() == 'exit':
            self.table.buffer[self.chat_id] = None
            self.table.states[self.chat_id] = State.NORMAL
            return "Alright, back into main menu"
        lst = text.split()
        nums = list()
        reply = str()
        for word in lst:
            try:
                nums.append(int(word))
            except:
                continue
        if nums:
            buff = self.table.buffer[self.chat_id]
            lst = list()
            for number in nums:
                if number <= len(buff) and number >= 1:
                    lst.append(buff[number - 1])
            if lst:
                reply = "Added these categories to your preferences: " + ', '.join(lst)
                self.table.buffer[self.chat_id] = None
                self.table.states[self.chat_id] = State.NORMAL
            else:
                reply = "Passed wrong numbers"
        else:
            reply = "Passed numbers in wrong format or didn't pass them at all"
        return reply