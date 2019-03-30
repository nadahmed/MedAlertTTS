from gtts import gTTS
import os, time
from googletrans import Translator
import asyncio
import schedule
import pyrebase
import secrets
from pygame import mixer
import subprocess

medicine={}

def stream_handler(message):
    global medicine
    path = str(message['path']).rsplit('/',1)[1]
    if message['event']=='patch':
        for k in message['data']:
            medicine[path][k]= message['data'][k]
        text =u'আচ্ছা।'
        speak(text)
    if message['event']=='put':
        for key in message['data']:
            if path == '':
                medicine = message['data']
            else:
                medicine[path] = message['data']
        text = u'আমি এখন up to date!'
        speak(text)
    # print(medicine.encode('utf-8'))
    # print(medicine)
    scheduler(medicine)
    print('\n')
        

def getData(email,password):
    print('INITIALIZING FIREBASE')
    firebase = pyrebase.initialize_app(secrets.config)
    print('Signing up')
    user = firebase.auth().sign_in_with_email_and_password(email,password)
    db = firebase.database()
    print('Fetching database')
    ref = db.child('users', user['localId'], 'medicines')
    ref.stream(stream_handler)



def wait(mixer): 
    while mixer.music.get_busy():
        pass
        
def speak(text):

    
    with open('file.txt', 'w+', encoding="utf-8") as f:
        f.write(text)
    mixer.init()
    i=0
    while 1:
        try:
            print('Fetching from TTS & Saving')
            subprocess.run("gtts-cli --file file.txt --lang bn --output temp.mp3", shell=True )
            # tts = gTTS(text=text, lang='bn')
            # print('saving')
            # tts.save('temp.mp3')
            break
        except Exception as e:
            i+=1
            print(e)
            if i==3:
                break
            continue
    print('\nTrying to speak\n')
    mp3 = mixer.music.load('temp.mp3')
    mixer.music.play()
    wait(mixer)
    mixer.music.load('temp2.mp3')
    mixer.quit()

async def sch():
    while 1:
        await asyncio.sleep(0)
        schedule.run_pending()

async def main():
    print('Time: {}'.format(time.process_time()))
    docs = getData(secrets.username, secrets.password)

def scheduler(meds):
    schedule.clear()
    for k in meds:
        name = meds[k]['name']
        notes = meds[k]['notes']
        time = meds[k]['time']
        checked = meds[k]['isChecked']
        
        for t in time:
            if checked:
                text = sch_textmaker(name,t['beforeMeal'],notes)
                # schedule.every(15).seconds.do(speak, text = text) # for debugging
                schedule.every().day.at(t['time']).do(speak, text = text)

def sch_textmaker(name , myTime, notes):
    text= u'আপনার ঔষধ খাবার সময় হয়েছে।'
    text+= u'ঔষধ এর নাম ' + name + '।'
    if myTime:
        text+=u'ঔষধ টি খাবেন খালি পেট এ।'
    else:
        text+=u'ঔষধ খাবার আগে কিছু খেয়ে নিবেন।'
    if notes != '':
        text+= u' এবং সাথে আপনার কিছু নোট। যা হচ্চে, '+ notes + u'।'
    return text
    # translator = Translator()
    # text = translator.translate(text, dest='bn').text

if __name__ == "__main__":
   
    loop = asyncio.get_event_loop()
    loop.create_task(sch())
    loop.create_task(main())
    loop.run_forever()
    # loop.run_until_complete(main())
    # asyncio.run(main())
        
    

