from enum import Enum
from bot import TelegramBot

class CallbackType(Enum):
    NONE = 1
    SELECT_PREFRENCES = 2
    CHOOSE_DATABASES = 3
    CONFIRM_VOICEMSG = 4

class Callback:
    def __init__(self):
        self.state = dict()
    
    def formReply(self, message, chat_id, bot):
        if self.state[chat_id] == CallbackType.NONE:
            self.react_normaly(message, chat_id, bot)
        elif self.state[chat_id] == CallbackType.SELECT_PREFRENCES:
            self.select_prefs(message, chat_id, bot)
        elif self.state[chat_id] == CallbackType.CHOOSE_DATABASES:
            self.choose_db(message, chat_id, bot)
        elif self.state[chat_id] == CallbackType.CONFIRM_VOICEMSG:
            self.voicemsg_work(message, chat_id, bot)
        else:
            print("Error occured")

    def react_normaly(self, message, chat_id, bot):
        if "voice" in message["message"]:
            file_id = message["message"]["voice"]["file_id"]
            aw = bot.audio_worker
            aw = audio_worker.AudioWorker()
            aw.prepare_dir(chat_id)

            #current_time = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
            ogg_file_path = bot.download_audio_file(chat_id, file_id)
            output = aw.ogg_to_mp3(ogg_file_path)
            text = aw.get_text(output)
            cat = bot.parse_and_lookup(text)
            print(cat)
            if cat:
                text = 'Adding this categories, am I right?\n'
                for number, category in enumerate(cat):
                    text += str(number + 1) + ') ' + category + '\n'
            self.state[chat_id] = CallbackType.CONFIRM_VOICEMSG
        else:
            text = message["message"]["text"]
            if self.state[chat_id] != CallbackType.CONFIRM_VOICEMSG:
                if text == "/selectpreferences":
                    self.state[chat_id] = CallbackType.SELECT_PREFRENCES
                elif text == "/choosedatabases":
                    self.state[chat_id] = CallbackType.CHOOSE_DATABASES
                else:
                    

    def select_prefs(self, message, chat_id, bot):

    def choose_db(self, message, chat_id, bot):

    def voicemsg_work(self, message, chat_id, bot):