from flask import Flask, render_template, request, redirect, url_for, session
from flask_session import Session
import secrets,uuid, random, os
import speech_recognition as srecog
from gtts import gTTS
from pydub import AudioSegment
from flask_talisman import Talisman

r = srecog.Recognizer()

def wav2flac(wav_path):
    flac_path = "%s.flac" % os.path.splitext(wav_path)[0]
    song = AudioSegment.from_wav(wav_path)
    song.export(flac_path, format = "flac")


def convert_to_audio(text):
    x = uuid.uuid1()
    audio = gTTS(text=text, lang='en', tld='com')
    name = f"static/{x}.wav"
    audio.save(name)
    return x

secret = secrets.token_urlsafe(32)

app = Flask(__name__)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.secret_key = secret
Session(app)
Talisman(app,content_security_policy=None)

@app.route('/test', methods=['GET'])
def test():
    print(session['defs'])
    session['rand'] = random.randint(0,len(session['defs']))
    print(session['rand'])
    name = convert_to_audio(session['defs'][session['rand']])
    return render_template('test.html',content=f"/static/{name}.wav", points=session['points'], sound=session['sound2'])

@app.route('/test', methods=['POST'])
def test2():
    if request.method == "POST":
        print(session['rand'])
        z = uuid.uuid1()
        file = request.files['file']
        f = open(f"audio/{z}.wav",'wb')
        f.write(file.read())
        f.close()
        os.system(f'ffmpeg -i audio/{z}.wav -acodec pcm_s16le -ac 1 -ar 16000 audio/{z}t.wav')
        audio = srecog.AudioFile(f"audio/{z}t.wav")
        with audio as source:
            audioData = r.record(source)
        print([r.recognize_google(audioData).lower()])
        print([session['terms'][session['rand']].lower()])
        if r.recognize_google(audioData).lower() == session['terms'][session['rand']].lower().strip():
            session['points'] += 1
            session['sound2'] = 'static/right.mp3'
        else:
            session['points'] -= 1
            session['sound2'] = 'static/wrong.mp3'
    return redirect('/test')

@app.route('/', methods=['GET'])
def home2():
    if request.method == 'GET': 
        print('called')
        return render_template('home.html')

@app.route('/', methods=['GET','POST'])
def home():
    session['sound2'] = 0
    session['points'] = 0
    session['test2'] = 'test'
    session['defs'] = []
    session['terms'] = []
    if request.method == 'POST':
        link = request.form['name']
        z = link.split('_')
        for i in z:
            try:
                i = i.split('~')
                session['defs'].append(i[1])
                session['terms'].append(i[0])
            except IndexError:
                pass
    return redirect('/test')

if __name__ == '__main__':
    app.run(host='0.0.0.0')