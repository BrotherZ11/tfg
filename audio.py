import librosa
import numpy as np
import matplotlib.pyplot as plt
import pretty_midi
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
from music21 import stream, note, meter, tempo

def cargar_audio(filepath):
    y, sr = librosa.load(filepath, sr=None)
    return y, sr

def extraer_caracteristicas(y, sr):
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    mel_spec = librosa.feature.melspectrogram(y=y, sr=sr)
    return mfccs, mel_spec

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
y, sr = cargar_audio('HesaPirate.mp3')
mfccs, mel_spec = extraer_caracteristicas(y, sr)
visualizar_caracteristicas(mfccs, mel_spec)

midi_data = cargar_midi('HesaPirate.mid')
notas = midi_a_notas(midi_data, sr)
print(notas)

def crear_dataset(y, sr, notas, ventana=2048, salto=512):
    X = []
    y_labels = []
    for nota in notas:
        pitch, start_sample, end_sample = nota
        for i in range(start_sample, end_sample, salto):
            segmento = y[i:i+ventana]
            if len(segmento) == ventana:
                mfcc = librosa.feature.mfcc(y=segmento, sr=sr, n_mfcc=13).flatten()
                X.append(mfcc)
                y_labels.append(pitch)
    return np.array(X), np.array(y_labels)

# Crear dataset
X, y_labels = crear_dataset(y, sr, notas)
print(f'X shape: {X.shape}, y shape: {y_labels.shape}')

# Crear el modelo
def crear_modelo(input_shape):
    modelo = Sequential([
        Dense(256, activation='relu', input_shape=input_shape),
        Dropout(0.3),
        Dense(256, activation='relu'),
        Dropout(0.3),
        Dense(128, activation='relu'),
        Dropout(0.3),
        Dense(88, activation='softmax')  # 88 teclas de piano
    ])
    modelo.compile(optimizer='adam', loss='sparse_categorical_crossentropy', metrics=['accuracy'])
    return modelo

# Entrenar el modelo
modelo = crear_modelo((X.shape[1],))
modelo.fit(X, y_labels, epochs=50, batch_size=32, validation_split=0.2)

def predecir_notas(modelo, y, sr, ventana=2048, salto=512):
    predicciones = []
    for i in range(0, len(y) - ventana, salto):
        segmento = y[i:i+ventana]
        if len(segmento) == ventana:
            mfcc = librosa.feature.mfcc(y=segmento, sr=sr, n_mfcc=13).flatten().reshape(1, -1)
            prediccion = modelo.predict(mfcc)
            nota = np.argmax(prediccion)
            predicciones.append((nota, i, i+ventana))
    return predicciones

# Cargar nuevo archivo de audio y predecir notas
nuevo_y, nuevo_sr = cargar_audio('HesaPirate.mp3')
predicciones = predecir_notas(modelo, nuevo_y, nuevo_sr)
print(predicciones)

def redondear_duracion(duracion):
    # Definir las duraciones musicales comunes en negras
    duraciones_comunes = [1, 2, 4, 8, 16]
    # Encontrar la duración más cercana
    duracion_redondeada = min(duraciones_comunes, key=lambda x: abs(x - duracion))
    return duracion_redondeada

def generar_partitura(predicciones):
    s = stream.Stream()
    # Agregar un compás y un tempo para facilitar la conversión
    s.append(meter.TimeSignature('4/4'))
    s.append(tempo.MetronomeMark(number=120))
    for p in predicciones:
        pitch, start_sample, end_sample = p
        duracion = librosa.samples_to_time(end_sample - start_sample, sr=sr)
        duracion_redondeada = redondear_duracion(duracion)
        n = note.Note(pitch, quarterLength=duracion_redondeada)
        s.append(n)
    return s

# Generar la partitura
partitura = generar_partitura(predicciones)

# Mostrar la partitura en una ventana interactiva
partitura.show()
