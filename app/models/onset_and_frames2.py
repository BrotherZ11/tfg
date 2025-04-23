import subprocess
import os

def transcribe_with_onset_and_frame(audio_path, output_dir, model_dir):
    """
    Usa el modelo Onset and Frames para convertir un archivo de audio a MIDI.
    
    Args:
        audio_path (str): Ruta del archivo de audio (.wav o .mp3).
        output_dir (str): Directorio donde se guardará el MIDI.
        model_dir (str): Directorio que contiene el checkpoint del modelo.
    
    Returns:
        str: Ruta del archivo MIDI generado.
    """
    midi_filename = os.path.basename(audio_path).replace(".mp3", ".mid").replace(".wav", ".mid")
    midi_path = os.path.join(output_dir, midi_filename)

    try:
        # Ejecutar el comando Onset and Frames
        subprocess.run([
            "onsets_frames_transcription_transcribe",
            f"--model_dir={model_dir}",
            audio_path
        ], check=True)
        return midi_path
    except subprocess.CalledProcessError as e:
        print(f"Error al ejecutar Onset and Frames: {e}")
        return None
