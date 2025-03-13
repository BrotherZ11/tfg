import mido
import numpy as np
import mir_eval
import pretty_midi
import pandas as pd


def load_midi_notes(midi_path):
    midi_data = pretty_midi.PrettyMIDI(midi_path)
    notes = []
    for instrument in midi_data.instruments:
        for note in instrument.notes:
            notes.append((note.start, note.end, note.pitch, note.velocity))
    notes = np.array(notes)
    intervals = notes[:, :2]  # [start, end]
    pitches = notes[:, 2]  # pitch
    return intervals, pitches


def preprocess_notes(intervals, pitches, min_duration=0.05):
    """Elimina notas muy cortas y solapadas."""
    cleaned_intervals = []
    cleaned_pitches = []

    for i, (onset, offset) in enumerate(intervals):
        duration = offset - onset
        # Filtrar notas cortas
        if duration > min_duration:
            cleaned_intervals.append([onset, offset])
            cleaned_pitches.append(pitches[i])

    return np.array(cleaned_intervals), np.array(cleaned_pitches)


def quantize_notes(intervals, grid_size=0.05):
    """Cuantiza los onsets y offsets a una rejilla temporal."""
    quantized_intervals = []
    for onset, offset in intervals:
        quantized_onset = round(onset / grid_size) * grid_size
        quantized_offset = round(offset / grid_size) * grid_size
        quantized_intervals.append([quantized_onset, quantized_offset])
    return np.array(quantized_intervals)


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


def evaluate_transcription(ref_intervals, ref_pitches, est_intervals, est_pitches,
                           onset_tol=0.05, pitch_tol=50):
    """Calcula Precision, Recall y F1 con preprocesamiento y cuantización."""
    # Preprocesamiento: limpiar y cuantizar
    est_intervals, est_pitches = preprocess_notes(est_intervals, est_pitches)
    est_intervals = quantize_notes(est_intervals)

    # Precision, Recall y F1-Score
    precision, recall, f1, _ = mir_eval.transcription.precision_recall_f1_overlap(
        ref_intervals, ref_pitches, est_intervals, est_pitches,
        onset_tolerance=onset_tol, pitch_tolerance=pitch_tol
    )
    
    # Evaluación de Onsets (50ms de tolerancia)
    onset_precision, onset_recall, onset_f1 = mir_eval.transcription.onset_precision_recall_f1(
        ref_intervals, est_intervals, onset_tolerance=onset_tol
    )

    # Frame Accuracy
    frame_accuracy = calculate_frame_accuracy(ref_intervals, est_intervals)

    return {
        "Precision": precision,
        "Recall": recall,
        "F1-Score": f1,
        "Onset Precision": onset_precision,
        "Onset Recall": onset_recall,
        "Onset F1-Score": onset_f1,
        "Frame Accuracy": frame_accuracy
    }


# Rutas a los archivos MIDI
ref_intervals, ref_pitches = load_midi_notes('output/midi/ground_truth/prueba.mid')
onsets_intervals, onsets_pitches = load_midi_notes('output/midi/onsets_and_frames/prueba.mid')
basic_intervals, basic_pitches = load_midi_notes('output/midi/basic_pitch/prueba.mid')
transkun_intervals, transkun_pitches = load_midi_notes('output/midi/transkun/prueba.mid')

# Evaluar cada modelo
results_onsets_frames = evaluate_transcription(ref_intervals, ref_pitches, onsets_intervals, onsets_pitches)
results_basic_pitch = evaluate_transcription(ref_intervals, ref_pitches, basic_intervals, basic_pitches)
results_transkun = evaluate_transcription(ref_intervals, ref_pitches, transkun_intervals, transkun_pitches)

# Mostrar resultados
df = pd.DataFrame([results_onsets_frames, results_basic_pitch, results_transkun],
                  index=["Onsets & Frames", "Basic Pitch", "Transkun"])
print(df)
