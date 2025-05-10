# src/audio_processing.py
from pydub import AudioSegment
import os
import sys

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
def convert_to_wav(input_audio_path):
    if os.path.exists(input_audio_path):
        sound = AudioSegment.from_mp3(input_audio_path)
        sound = sound.set_frame_rate(16000).set_channels(1)
        wav_path = input_audio_path.replace(".mp3", ".wav")
        sound.export(wav_path, format="wav")
        return wav_path
    else:
        raise FileNotFoundError(f"El archivo {input_audio_path} no existe.")
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python preprocess.py <ruta_del_audio_mp3>")
    else:
        ruta = os.path.join(ROOT_DIR, sys.argv[1])

        try:
            archivo_wav = convert_to_wav(ruta)
            print(f"Archivo convertido a WAV: {archivo_wav}")
        except Exception as e:
            print(f"Error: {e}")

#input_audio_path="./data/input/chopin.mp3"