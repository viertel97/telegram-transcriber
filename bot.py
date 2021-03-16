from telegram.ext.dispatcher import run_async
from telegram import ChatAction
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import speech_recognition as sr 
import subprocess
import os
import todoist
from datetime import datetime

chat_id = 123456789
r = sr.Recognizer()
api = todoist.TodoistAPI('API-KEY')
token = 'TELEGRAM-TOKEN'

def start(update: Update, context: CallbackContext):
    update.message.reply_text(text="Say stuff, I'll transcribe")


def voice_to_text(update: Update, context: CallbackContext):
    file_name = str(chat_id) + '_' + str(update.message.from_user.id) + str(update.message.message_id) + '.ogg'
    update.message.voice.get_file().download(file_name)
    file_path = os.path.abspath(file_name)
    print(file_path)

    modification_date = datetime.fromtimestamp(os.path.getmtime(file_path)).strftime("%d-%m-%Y-%H:%M:%S")
    wav_converted_file_path = file_path + '.wav'
    wav_cmd = 'ffmpeg -i "' + file_path + '" -ar 48000 "' + wav_converted_file_path + '"'
    subprocess.call(wav_cmd, shell=True)
    r_file = sr.AudioFile(wav_converted_file_path)
    with r_file as source:
        audio = r.record(source)
    recognized_text = r.recognize_google(audio, language ='de-DE')
    finalMessage = modification_date + " : " + recognized_text

    update.message.reply_text(finalMessage)
    sendToTodoist(finalMessage)
    os.remove(file_name)
    os.remove(wav_converted_file_path)
def sendToTodoist(message):
  api.items.add(message)
  test = api.commit()

def main():
    api.sync()
    updater = Updater(token=token, use_context= True)
    dispatcher = updater.dispatcher
    start_handler = CommandHandler(str('start'), start)
    oh_handler = MessageHandler(Filters.voice, voice_to_text)
    dispatcher.add_handler(start_handler)
    dispatcher.add_handler(oh_handler)
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
