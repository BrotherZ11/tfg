import subprocess
import os
import sys
from music21 import converter

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

def convert_midi_to_pdf_with_musescore(midi_path, output_dir, musescore_path="C:/Program Files/MuseScore 4/bin/MuseScore4.exe"):
    """
    Convierte un archivo MIDI a PDF usando MuseScore.
    """
    pdf_path = os.path.join(output_dir, os.path.basename(midi_path).replace(".mid", ".pdf"))
    try:
        result = subprocess.run(
            [musescore_path, midi_path, '-o', pdf_path],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        return pdf_path
    except FileNotFoundError:
        raise RuntimeError("MuseScore no está instalado o no se encuentra en la ruta especificada.")
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"Error al convertir MIDI a PDF con MuseScore: {e.stderr.decode()}")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Uso: python generate_score.py <ruta_midi> <directorio_salida>")
    else:
        midi_file = os.path.join(ROOT_DIR, sys.argv[1])
        output_folder = os.path.join(ROOT_DIR, sys.argv[2])
        os.makedirs(output_folder, exist_ok=True)

        try:
            pdf = convert_midi_to_pdf_with_musescore(midi_file, output_folder)
            print(f"PDF generado con éxito: {pdf}")
        except Exception as e:
            print(f"Error: {e}")



# def generate_score(midi_path, output_path):
#     """
#     Convierte un archivo MIDI a MusicXML (formato compatible con MuseScore).
#     """
#     score = converter.parse(midi_path)
#     score.makeMeasures(inPlace=True)
#     score.splitAtDurations()
#     score.write('musicxml', fp=output_path, makeNotation=True)
#     return output_path

# if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print("Uso: python convert_midi_to_musicxml.py <midi_path> <output_dir>")
#     else:
#         audio = os.path.join(ROOT_DIR, sys.argv[1])
#         output = os.path.join(ROOT_DIR, sys.argv[2])
#         result = generate_score(audio, output)
#         if result:
#             print(f"Archivo XML generado: {result}")
#         else:
#             print("Falló la transcripción con Transkun.")