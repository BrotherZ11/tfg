import librosa
import numpy as np
import matplotlib.pyplot as plt
import pretty_midi

def cargar_audio(filepath):
    y, sr = librosa.load(filepath, sr=None)
    return y, sr

def extraer_caracteristicas(y, sr):
    # Extraer MFCCs y un espectrograma
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
    return mfccs, mel_spec

# Visualización de características
def visualizar_caracteristicas(mfccs, mel_spec):
    plt.figure(figsize=(10, 4))
    plt.subplot(2, 1, 1)
    librosa.display.specshow(mfccs, x_axis='time')
    plt.colorbar()
    plt.title('MFCC')

    plt.subplot(2, 1, 2)
    librosa.display.specshow(librosa.power_to_db(mel_spec, ref=np.max), x_axis='time', y_axis='mel')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Mel Spectrogram')

    plt.tight_layout()
    plt.show()

def cargar_midi(filepath):
    midi_data = pretty_midi.PrettyMIDI(filepath)
    return midi_data

def midi_a_notas(midi_data, sr):
    notas = []
    for instrumento in midi_data.instruments:
        for nota in instrumento.notes:
            start_sample = librosa.time_to_samples(nota.start, sr=sr)
            end_sample = librosa.time_to_samples(nota.end, sr=sr)
            notas.append((nota.pitch, start_sample, end_sample))
    return notas


# Ejemplo de uso
y, sr = cargar_audio('Titantic.mp3')
mfccs, mel_spec = extraer_caracteristicas(y, sr)
visualizar_caracteristicas(mfccs, mel_spec)

midi_data = cargar_midi('Titantic.mid')
notas = midi_a_notas(midi_data, sr)
print(notas)
