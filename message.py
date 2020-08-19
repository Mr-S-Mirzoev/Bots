from abc import ABC, abstractmethod
from audio_worker import AudioWorker
import requests, json, urllib, os
from callback import CallbackWorker

class Attachment(ABC):
    def __init__(self, chat_id):
        self.chat_id = chat_id

    @abstractmethod
    def __str__(self):
        pass

class Audio(Attachment):
    def __init__(self, chat_id, file_id, token):
        super().__init__(chat_id)
        self.file_id = file_id
        self.text = str()
        self.token = token
        self.aw = AudioWorker()

    def get_url(self, url):
        response = requests.get(url)
        content = response.content.decode("utf8")
        return content

    def get_json_from_url(self, url):
        content = self.get_url(url)
        js = json.loads(content)
        return js

    def download_audio_file(self, chat_id, file_id):
        js = self.get_json_from_url("https://api.telegram.org/bot{}/getFile?file_id={}".format(self.token, file_id))
        file_path = js["result"]["file_path"]
        source = os.path.join('./files/{}'.format(chat_id), file_path)
        urllib.request.urlretrieve("https://api.telegram.org/file/bot{}/{}".format(self.token, file_path), source)
        return source

    def __str__(self):
        try:
            self.aw.prepare_dir(self.chat_id)
            ogg_file_path = self.download_audio_file(self.chat_id, self.file_id)
            mp3_file_path = self.aw.ogg_to_mp3(ogg_file_path)
            text = self.aw.get_text(mp3_file_path)
            return text
        except:
            return "Error during parsing voice message"

class Text(Attachment):
    def __init__(self, chat_id, text):
        super().__init__(chat_id)
        self.value = text

    def __str__(self):
        return self.value

class Message:
    def __init__(self, message: dict, chat_id, token, statetable):
        self.attachments = list()
        self.chat_id = chat_id
        self.statetable = statetable
        keys = message.keys()
        if 'text' in keys:
            self.attachments.append(Text(chat_id, message['text']))
        elif 'voice' in keys:
            self.attachments.append(Audio(chat_id, message['voice']['file_id'], token))

    def reply(self):
        for attachment in self.attachments:
            txt_val = str(attachment)
            cw = CallbackWorker()
            reply = cw.act(txt_val, self.statetable, self.chat_id)
            print(self.statetable.states[self.chat_id])
            yield reply