
import numpy as np
import mir_eval
import pretty_midi
import librosa
import librosa.display
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

def load_midi(file_path):
    midi_data = pretty_midi.PrettyMIDI(file_path)
    
    notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.pitch, note.end))
    
    # Ordena por el onset (inicio de la nota)
    notes.sort(key=lambda x: x[0])
    
    # Separa en listas
    onsets = np.array([n[0] for n in notes])
    pitches = np.array([n[1] for n in notes])
    offsets = np.array([n[2] for n in notes])
    
    return pitches, onsets, offsets

def calculate_frame_accuracy(ref_intervals, est_intervals, frame_size=0.01):
    """Calcula el Frame Accuracy dividiendo el tiempo en frames de frame_size."""
    max_time = max(ref_intervals[-1, 1], est_intervals[-1, 1])  # Duración total
    frames = np.arange(0, max_time, frame_size)  # Dividimos el tiempo en frames

    # Crear arrays de activación por frames
    ref_active = np.zeros(len(frames))
    est_active = np.zeros(len(frames))

    # Marcar frames activos en la referencia
    for onset, offset in ref_intervals:
        ref_active[(frames >= onset) & (frames <= offset)] = 1

    # Marcar frames activos en la estimación
    for onset, offset in est_intervals:
        est_active[(frames >= onset) & (frames <= offset)] = 1

    # Calcular Frame Accuracy: frames coincidentes / total de frames activos
    matching_frames = np.sum(ref_active == est_active)
    frame_accuracy = matching_frames / len(frames)
    return frame_accuracy


def calculate_metrics(reference_file, model_file):
    # Cargar referencia y modelo
    ref_pitches, ref_onsets, ref_offsets = load_midi(reference_file)
    model_pitches, model_onsets, model_offsets = load_midi(model_file)

    # Crear intervalos onset-offset
    ref_intervals = np.column_stack((ref_onsets, ref_offsets))
    model_intervals = np.column_stack((model_onsets, model_offsets))

    # Onset metrics
    onset_precision, onset_recall, onset_f1 = mir_eval.transcription.onset_precision_recall_f1(ref_intervals, model_intervals)
    
    # Offset metrics
    offset_precision, offset_recall, offset_f1 = mir_eval.transcription.offset_precision_recall_f1(ref_intervals, model_intervals)
    
    # Overlap metrics (onset + pitch + offset)
    overlap_precision, overlap_recall, overlap_f1, avg_overlap_ratio = mir_eval.transcription.precision_recall_f1_overlap(
        ref_intervals, ref_pitches, model_intervals, model_pitches
    )

    # Frame Accuracy
    frame_accuracy = calculate_frame_accuracy(ref_intervals, model_intervals)

    # Resultados
    return {
        'Onset Precision': onset_precision,
        'Onset Recall': onset_recall,
        'Onset F1': onset_f1,
        'Offset Precision': offset_precision,
        'Offset Recall': offset_recall,
        'Offset F1': offset_f1,
        'Overlap Precision': overlap_precision,
        'Overlap Recall': overlap_recall,
        'Overlap F1': overlap_f1,
        'Average Overlap Ratio': avg_overlap_ratio,
        "Frame Accuracy": frame_accuracy
    }



def plot_piano_roll(pitches, onsets, offsets, title="Piano Roll"):
    plt.figure(figsize=(12, 6))
    plt.scatter(onsets, pitches, color='royalblue', label='Onset', s=50)
    plt.scatter(offsets, pitches, color='tomato', label='Offset', s=50, marker='x')
    plt.xlabel('Time (s)')
    plt.ylabel('Pitch (MIDI Note)')
    plt.title(title)
    plt.legend()
    plt.grid(True)
    plt.show()
    
# Rutas a los archivos MIDI
reference_file = 'output/midi/ground_truth/pachelbel-canon-in-d.mid'
onset_frame_file = 'output/midi/onsets_and_frames/pachelbel-canon-in-d.mid'
basic_pitch_file = 'output/midi/basic_pitch/pachelbel-canon-in-d_basic_pitch.mid'
transkun_file = 'output/midi/transkun/pachelbel-canon-in-d_transkun.mid'
# Evaluar cada modelo
# Calcula métricas
models = {
    'Onset and Frame': calculate_metrics(reference_file, onset_frame_file),
    'Basic Pitch': calculate_metrics(reference_file, basic_pitch_file),
    'Transkun': calculate_metrics(reference_file, transkun_file)
}

# Muestra métricas
import pandas as pd
df = pd.DataFrame(models).T
print(df)

# Visualización de los resultados
ref_pitches, ref_onsets, ref_offsets = load_midi(reference_file)
plot_piano_roll(ref_pitches, ref_onsets, ref_offsets, title="Ground Truth")

for model, midi_file in [('Onset and Frame', onset_frame_file), 
                         ('Basic Pitch', basic_pitch_file), 
                         ('Transkun', transkun_file)]:
    pitches, onsets, offsets = load_midi(midi_file)
    plot_piano_roll(pitches, onsets, offsets, title=model)

metrics = ['Onset Precision', 'Onset Recall', 'Onset F1',
               'Offset Precision', 'Offset Recall', 'Offset F1']

# Gráfico de barras para precisión, recall y F1 en onsets y offsets
df[metrics].plot(kind='bar', figsize=(12, 6), title='Onset and Offset Metrics')
plt.ylabel('Score')
plt.xlabel('Models')
plt.legend(title='Metrics', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.show()


# Radar plot
labels = np.array(metrics + ['Overlap Precision', 'Overlap Recall', 'Overlap F1'])
num_vars = len(labels)

angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
angles += angles[:1]

fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
for model in df.index:
    values = df.loc[model, labels].tolist()
    values += values[:1]
    ax.plot(angles, values, label=model)
    ax.fill(angles, values, alpha=0.25)

ax.set_yticklabels([])
ax.set_xticks(angles[:-1])
ax.set_xticklabels(labels, fontsize=10)
plt.legend(loc='upper right', bbox_to_anchor=(1.1, 1.1))
plt.show()