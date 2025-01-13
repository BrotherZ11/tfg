import pretty_midi

def clean_midi_file(input_midi_path, output_midi_path):
    midi_data = pretty_midi.PrettyMIDI(input_midi_path)
    midi_data.write(output_midi_path)
    return output_midi_path

# Uso:
cleaned_midi_path = clean_midi_file("output.mid", "archivo_limpio.mid")
