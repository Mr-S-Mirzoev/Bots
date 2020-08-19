from enum import Enum

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