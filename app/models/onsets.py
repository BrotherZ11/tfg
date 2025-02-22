import os
import tensorflow as tf
import numpy as np
from magenta.models.onsets_frames_transcription import data
from magenta.models.onsets_frames_transcription import configs
from magenta.models.onsets_frames_transcription import train_util
from magenta.music import sequences_lib
from magenta.music import midi_io
from magenta.protobuf import music_pb2
import note_seq

class MagentaTranscriber:
    def __init__(self, checkpoint_path):
        """
        Inicializa el transcriptor usando el modelo Onsets and Frames.
        
        Args:
            checkpoint_path (str): Ruta al checkpoint del modelo pre-entrenado
        """
        self.config = configs.CONFIG_MAP['onsets_frames']
        self.hparams = self.config.hparams
        self.hparams.batch_size = 1
        self.hparams.truncated_length_secs = 0
        
        # Construir el modelo
        self.estimator = train_util.create_estimator(
            config=self.config,
            model_dir=checkpoint_path,
            save_summary_steps=0,
            save_checkpoints_steps=None
        )

    def preprocess_audio(self, audio_path):
        """
        Preprocesa el archivo de audio para el modelo.
        
        Args:
            audio_path (str): Ruta al archivo de audio
            
        Returns:
            examples: Datos preprocesados para el modelo
        """
        # Crear un ejemplo de datos
        example = data.preprocess_example(
            audio_path,
            hparams=self.hparams,
            is_training=False
        )
        
        return example

    def transcribe(self, audio_path, output_midi_path, min_velocity=0):
        """
        Transcribe un archivo de audio a MIDI.
        
        Args:
            audio_path (str): Ruta al archivo de audio de entrada
            output_midi_path (str): Ruta donde guardar el archivo MIDI
            min_velocity (int): Velocidad mínima para considerar una nota (0-127)
        """
        # Preprocesar audio
        example = self.preprocess_audio(audio_path)
        
        # Predicción
        predict_fn = self.estimator.predict(
            input_fn=lambda: tf.data.Dataset.from_tensors(example)
        )
        
        sequence_prediction = next(predict_fn)
        
        # Convertir predicción a sequence proto
        sequence_pred = sequences_lib.pianoroll_to_note_sequence(
            frames=sequence_prediction['frame_predictions'][0],
            frames_per_second=data.hparams_frames_per_second(self.hparams),
            min_duration_ms=0,
            min_velocity=min_velocity
        )
        
        # Guardar como MIDI
        midi_io.note_sequence_to_midi_file(sequence_pred, output_midi_path)
        
        return sequence_pred

    def transcribe_to_musicxml(self, audio_path, output_xml_path, min_velocity=0):
        """
        Transcribe un archivo de audio a MusicXML.
        
        Args:
            audio_path (str): Ruta al archivo de audio de entrada
            output_xml_path (str): Ruta donde guardar el archivo MusicXML
            min_velocity (int): Velocidad mínima para considerar una nota (0-127)
        """
        # Primero transcribimos a MIDI
        sequence = self.transcribe(audio_path, "temp.mid", min_velocity)
        
        # Convertir sequence a pretty_midi
        pm = note_seq.sequence_proto_to_pretty_midi(sequence)
        
        # Usar music21 para convertir a MusicXML
        from music21 import converter
        score = converter.parse("temp.mid")
        score.write('musicxml', fp=output_xml_path)
        
        # Limpiar archivo temporal
        if os.path.exists("temp.mid"):
            os.remove("temp.mid")

def download_checkpoint():
    """
    Descarga el checkpoint pre-entrenado de Onsets and Frames si no existe.
    
    Returns:
        str: Ruta al checkpoint
    """
    import tensorflow_hub as hub
    
    # URL del modelo pre-entrenado
    MODEL_URL = "https://tfhub.dev/google/magenta/onsets-frames-piano/1"
    
    # Crear directorio para el checkpoint si no existe
    checkpoint_dir = "onsets_frames_checkpoint"
    if not os.path.exists(checkpoint_dir):
        os.makedirs(checkpoint_dir)
        
    # Descargar y extraer el modelo
    model = hub.load(MODEL_URL)
    
    return checkpoint_dir

def main():
    # Ejemplo de uso
    checkpoint_path = download_checkpoint()
    transcriber = MagentaTranscriber(checkpoint_path)
    
    # Transcribir archivo de audio
    audio_path = "piano_recording.wav"
    
    # Guardar como MIDI
    transcriber.transcribe(
        audio_path=audio_path,
        output_midi_path="transcribed_piano.mid",
        min_velocity=10  # Ajustar según necesidad
    )
    
    # Guardar como MusicXML
    transcriber.transcribe_to_musicxml(
        audio_path=audio_path,
        output_xml_path="transcribed_piano.musicxml",
        min_velocity=10
    )

if __name__ == "__main__":
    main()