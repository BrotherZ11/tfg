import pretty_midi
import librosa.display
import numpy as np
import matplotlib.pyplot as plt

def midi_to_wave(midi_file, sr=22050):
    """Convierte un archivo MIDI a una señal de audio (waveform) usando PrettyMIDI."""
    midi_data = pretty_midi.PrettyMIDI(midi_file)
    audio = midi_data.synthesize(fs=sr)  # Genera el audio directamente
    return audio, sr

def plot_waveform_and_spectrogram(audio, sr, title):
    """Genera y muestra la forma de onda y el espectrograma del audio."""
    plt.figure(figsize=(12, 6))
    
    # Forma de onda
    plt.subplot(2, 1, 1)
    librosa.display.waveplot(audio, sr=sr)
    plt.title(f'Forma de onda - {title}')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Amplitud')

    # Espectrograma
    plt.subplot(2, 1, 2)
    S = librosa.feature.melspectrogram(y=audio, sr=sr)
    S_dB = librosa.power_to_db(S, ref=np.max)
    librosa.display.specshow(S_dB, sr=sr, x_axis='time', y_axis='linear')
    plt.title(f'Espectrograma - {title}')
    plt.colorbar(label='Intensidad (dB)')

    plt.tight_layout()
    plt.show()

# Lista de archivos MIDI
files = {
    "Referencia": 'output/midi/ground_truth/prueba.mid',
    "Onset and Frame": 'output/midi/onsets_and_frames/prueba.mid',
    "Basic Pitch": 'output/midi/basic_pitch/prueba.mid',
    "Transkun": 'output/midi/transkun/prueba.mid'
}

# Procesar y graficar cada archivo
for model, file_path in files.items():
    audio, sr = midi_to_wave(file_path)
    plot_waveform_and_spectrogram(audio, sr, model)
