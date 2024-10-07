import pyttsx3
import speech_recognition as sr
import pyaudio
engine = pyttsx3.init('sapi5')
voices = engine.getProperty('voices')
engine.setProperty('voice',voices[0].id)
def speak(audio):
    engine.say(audio)
    engine.runAndWait()

def take_command():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.pause_threshold = 0.5
        audio = r.listen(source)

    try:
        print("listening")
        query=r.recognize_google(audio, language='en-in')
        print("user said:",query)

    except Exception as e:
        print("say that again please")
        return "none"


if __name__=="__main__":
    #speak("Hello Mr. Aaryan")
    speak("hi")
    take_command()
