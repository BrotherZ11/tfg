from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import os

def transcribe_with_basic_pitch(audio_path, output_dir):
    """
    Transcribe audio to MIDI using Basic Pitch.
    Args:
        audio_path (str): Path to the input WAV file.
        output_dir (str): Directory to save the output MIDI file.
    Returns:
        str: Path to the output MIDI file.
    """
    # Nombre del archivo MIDI de salida
    midi_path = os.path.join(output_dir, os.path.basename(audio_path).replace(".wav", "_basic_pitch.mid"))

    # Ejecutar la transcripción y guardar los archivos necesarios
    predict_and_save(
        [audio_path],  # Lista con el archivo de audio
        output_dir,  # Directorio de salida
        save_midi=True,  # Guardar MIDI
        sonify_midi=False,  # No generar audio del MIDI
        save_model_outputs=False,  # No guardar las salidas del modelo
        save_notes=False,  # No guardar notas separadas
        model_or_model_path=ICASSP_2022_MODEL_PATH  # Modelo preentrenado
    )
    
    # Verifica si se generó el archivo correctamente
    if os.path.exists(midi_path):
        return midi_path
    else:
        raise RuntimeError("No se pudo generar el archivo MIDI con Basic Pitch.")

#transcribe_with_basic_pitch("protegidos.wav", "./")


