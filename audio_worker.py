import requests
import speech_recognition as sr
from pydub import AudioSegment
import os

class AudioWorker:
    class __AW:
        def __init__(self):
            self.recogniser = sr.Recognizer()

        def prepare_dir(self, chat_id):
            if not os.path.isdir('./files'):
                os.mkdir('./files')
            if not os.path.isdir('./files/{}'.format(chat_id)):
                os.mkdir('./files/{}'.format(chat_id))
            if not os.path.isdir('./files/{}/voice'.format(chat_id)):
                os.mkdir('./files/{}/voice'.format(chat_id))
        
        def ogg_to_mp3(self, source):
            ogg_audio = AudioSegment.from_file(source, format="ogg")
            outputfile = '{}.wav'.format(source[:-4])
            ogg_audio.export(outputfile, format="wav")
            return outputfile

        def get_text(self, source):
            voice_message = sr.AudioFile(source)
            with voice_message as source:
                audio = self.recogniser.record(source)
            result = self.recogniser.recognize_google(audio)
            text = str(result).replace('p***', 'porn')
            return text

    instance = None
    def __init__ (self):
        if not AudioWorker.instance:
            print("AW: Not yet created, creating")
            AudioWorker.instance = AudioWorker.__AW()
        else:
            print("AW: Already created, using previous")

    def prepare_dir(self, chat_id):
        AudioWorker.instance.prepare_dir(chat_id)

    def ogg_to_mp3(self, source):
        return AudioWorker.instance.ogg_to_mp3(source)

    def get_text(self, source):
        return AudioWorker.instance.get_text(source)