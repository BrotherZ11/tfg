import tensorflow._api.v2.compat.v1 as tf
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
import os

tf.enable_v2_behavior()

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
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
    
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python basic_pitch.py <ruta_audio.wav> <directorio_salida>")
    else:
        audio = os.path.join(ROOT_DIR, sys.argv[1])
        output_dir = os.path.join(ROOT_DIR, sys.argv[2])
        os.makedirs(output_dir, exist_ok=True)
        try:
            midi_file = transcribe_with_basic_pitch(audio, output_dir)
            print(f"MIDI generado con éxito: {midi_file}")
        except Exception as e:
            print(f"Error durante la transcripción: {e}")

#transcribe_with_basic_pitch("test.wav", "./")


