import pretty_midi

def clean_midi(midi_path, min_note_duration=0.1, max_silence_duration=0.05):
    """
    Limpia un archivo MIDI eliminando notas demasiado cortas y silencios innecesarios.
    Args:
        midi_path (str): Ruta al archivo MIDI.
        min_note_duration (float): Duración mínima de las notas en segundos.
        max_silence_duration (float): Duración máxima de silencios que se pueden considerar.
    Returns:
        str: Ruta al archivo MIDI limpio.
    """
    midi_data = pretty_midi.PrettyMIDI(midi_path)
    
    # Filtrar notas cortas
    for instrument in midi_data.instruments:
        instrument.notes = [
            note for note in instrument.notes if (note.end - note.start) > min_note_duration
        ]
    
    # Guardar el archivo MIDI limpio
    cleaned_midi_path = midi_path.replace(".mid", "_clean.mid")
    midi_data.write(cleaned_midi_path)
    return cleaned_midi_path
