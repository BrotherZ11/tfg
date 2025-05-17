import subprocess
import os

def convert_midi_to_pdf_with_musescore(midi_path, output_dir, musescore_path="C:/Program Files/MuseScore 4/bin/MuseScore4.exe"):
    """
    Convierte un archivo MIDI a PDF usando MuseScore.
    """
    pdf_path = os.path.join(output_dir, os.path.basename(midi_path).replace(".mid", ".pdf"))
    try:
        # MuseScore para convertir MIDI a PDF
        subprocess.run(
            [musescore_path, midi_path, '-o', pdf_path],
            check=True
        )
        return pdf_path
    except subprocess.CalledProcessError as e:
        print(f"Error al convertir MIDI a PDF: {e}")
        return None
