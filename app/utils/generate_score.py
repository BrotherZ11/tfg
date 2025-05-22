import subprocess
import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

from music21 import converter

def generate_score(midi_path, output_path):
    """
    Convierte un archivo MIDI a MusicXML (formato compatible con MuseScore).
    """
    score = converter.parse(midi_path)
    score.makeMeasures(inPlace=True)
    score.splitAtDurations()
    score.write('musicxml', fp=output_path, makeNotation=True)
    return output_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python convert_midi_to_musicxml.py <midi_path> <output_dir>")
    else:
        audio = os.path.join(ROOT_DIR, sys.argv[1])
        output = os.path.join(ROOT_DIR, sys.argv[2])
        result = generate_score(audio, output)
        if result:
            print(f"Archivo XML generado: {result}")
        else:
            print("Falló la transcripción con Transkun.")