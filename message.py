from abc import ABC, abstractmethod
from bot import TelegramBot

class Attachment(ABC):
    def __init__(self, bot: TelegramBot, chat_id):
        self.chat_id = chat_id
        self.bot = bot

    @abstractmethod
    def __str__(self):
        pass

class Audio(Attachment):
    def __init__(self, bot: TelegramBot, chat_id, file_id):
        super().__init__(bot, chat_id)
        self.file_id = file_id
        self.text = str()

    def __str__(self):
        self.bot.audio_worker.prepare_dir(self.chat_id)
        ogg_file_path = self.bot.download_audio_file(self.chat_id, self.file_id)
        mp3_file_path = self.bot.audio_worker.ogg_to_mp3(ogg_file_path)
        return self.bot.audio_worker.get_text(mp3_file_path)

class Text(Attachment):
    def __init__(self, bot: TelegramBot, chat_id, text):
        super().__init__(bot, chat_id)
        self.value = text

    def __str__(self):
        return self.value

class Message:
    def __init__(self, bot: TelegramBot, message: dict, chat_id):
        self.attachments = list()
        self.bot = bot
        self.chat_id = chat_id
        keys = message.keys()
        if 'text' in keys:
            self.attachments.append(Text(bot, chat_id, message['text']))
        elif 'voice' in keys:
            self.attachments.append(Audio(bot, chat_id, message['voice']['file_id']))
        self.reply()

    def reply(self):
        for attachment in self.attachments:
            txt_val = str(attachment)
            self.bot.send_message("Replying to " + txt_val, self.chat_id)