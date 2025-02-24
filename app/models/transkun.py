import subprocess
import os

def transcribe_with_transkun(audio_path, output_dir):
    """
    Usa Transkun para convertir un archivo de audio a MIDI.
    
    Args:
        audio_path (str): Ruta del archivo de audio (.wav o .mp3).
        output_dir (str): Directorio donde se guardará el MIDI.
    
    Returns:
        str: Ruta del archivo MIDI generado.
    """
    midi_filename = os.path.basename(audio_path).replace(".mp3", ".mid").replace(".wav", "_transkun.mid")
    midi_path = os.path.join(output_dir, midi_filename)

    try:
        # Ejecutar el comando Transkun
        subprocess.run(["transkun", audio_path, midi_path], check=True)
        return midi_path
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar Transkun: {e}")
        return None
