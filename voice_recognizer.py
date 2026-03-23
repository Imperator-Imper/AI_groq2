import io
import speech_recognition as sr
from pydub import AudioSegment
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()
    
    async def recognize_ogg(self, ogg_data: bytes):
        try:
            audio = AudioSegment.from_ogg(io.BytesIO(ogg_data))
            wav_io = io.BytesIO()
            audio.export(wav_io, format="wav")
            wav_io.seek(0)
            
            with sr.AudioFile(wav_io) as source:
                audio_data = self.recognizer.record(source)
                try:
                    text = self.recognizer.recognize_google(audio_data, language="ru-RU")
                    return text
                except:
                    try:
                        text = self.recognizer.recognize_google(audio_data, language="en-US")
                        return text
                    except:
                        return None
        except Exception as e:
            logger.error(f"Voice error: {e}")
            return None

voice_recognizer = VoiceRecognizer()