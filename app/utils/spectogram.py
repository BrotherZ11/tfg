import pretty_midi
import librosa.display
import numpy as np
import matplotlib.pyplot as plt
import os
import sys
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

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

if __name__ == "__main__":
    # Rutas por defecto relativas al ROOT_DIR
    files = {
        "Referencia": os.path.join(ROOT_DIR, 'output/midi/ground_truth/prueba.mid'),
        "Onset and Frame": os.path.join(ROOT_DIR, 'output/midi/onsets_and_frames/prueba.mid'),
        "Basic Pitch": os.path.join(ROOT_DIR, 'output/midi/basic_pitch/prueba.mid'),
        "Transkun": os.path.join(ROOT_DIR, 'output/midi/transkun/prueba.mid')
    }

    # Si se pasan 4 argumentos, reemplazamos las rutas
    if len(sys.argv) == 5:
        files = {
            "Referencia": os.path.join(ROOT_DIR, sys.argv[1]),
            "Onset and Frame": os.path.join(ROOT_DIR, sys.argv[2]),
            "Basic Pitch": os.path.join(ROOT_DIR, sys.argv[3]),
            "Transkun": os.path.join(ROOT_DIR, sys.argv[4])
        }
    elif len(sys.argv) != 1:
        print("Uso:")
        print("  python visualize_audio.py")
        print("  python visualize_audio.py <ref.mid> <onset_and_frame.mid> <basic_pitch.mid> <transkun.mid>")
        sys.exit(1)

    # Procesar y graficar cada archivo
    for model, file_path in files.items():
        if not os.path.exists(file_path):
            print(f"❌ Archivo no encontrado: {file_path}")
            continue
        print(f"✅ Procesando: {model}")
        audio, sr = midi_to_wave(file_path)
        plot_waveform_and_spectrogram(audio, sr, model)