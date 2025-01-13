# from music21 import converter, instrument, note, chord, stream

# def midi_a_partitura(midi_file):
#     # Cargar el archivo MIDI
#     midi = converter.parse(midi_file)

#     # Separar las partes por instrumento
#     parts = instrument.partitionByInstrument(midi)

#     # Crear un stream vacío para almacenar las notas y acordes
#     partitura = stream.Score()

#     # Si hay varias partes por instrumento
#     if parts:  
#         for part in parts.parts:
#             # Iterar sobre los eventos del archivo MIDI
#             for elemento in part.recurse():
#                 # Si el evento es una nota, añadirla al stream de la partitura
#                 if isinstance(elemento, note.Note):
#                     print(f"Nota: {elemento}")
#                     partitura.append(elemento)
#                 # Si el evento es un acorde, añadirlo al stream de la partitura
#                 elif isinstance(elemento, chord.Chord):
#                     print(f"Acorde: {elemento}")
#                     partitura.append(elemento)
#     else:
#         # Si no hay partes instrumentales, iterar sobre el midi directamente
#         for elemento in midi.flat.notes:
#             print(f"Elemento: {elemento}")
#             partitura.append(elemento)

#     # Intentar corregir la notación (esto puede resolver algunos problemas)
#     try:
#         partitura.makeNotation(inPlace=True)
#     except Exception as e:
#         print(f"Error corrigiendo la notación: {e}")

#     # Mostrar la partitura en formato texto
#     partitura.show('text')
    

#     # Guardar la partitura en formato MusicXML
#     try:
#         partitura.write('pdf', fp='partitura.pdf')
#         print("Partitura guardada correctamente.")
#     except Exception as e:
#         print(f"Error guardando la partitura: {e}")

# # Ruta del archivo MIDI
# archivo_midi = 'hola.mid'

# # Convertir a partitura
# midi_a_partitura(archivo_midi)
import os
from music21 import converter, environment

env = environment.UserSettings()
us = environment.UserSettings()
env['lilypondPath'] = 'C:/lilypond/bin/lilypond.exe'
us['musescoreDirectPNGPath'] = 'C:/Program Files/MuseScore 4/bin/MuseScore4.exe'  # Cambia por la ruta a MuseScore en tu sistema

from music21 import converter, note, chord

def clean_midi(midi_path):
    # Cargar el archivo MIDI
    score = converter.parse(midi_path)

    # Recorrer todas las partes y notas
    for part in score.parts:
        for element in part.flat.notesAndRests:
            if isinstance(element, note.Rest):  # Si es un silencio
                # Buscar las notas que se solapan con este silencio
                overlapping_notes = [n for n in part.flat.notes if n.offset == element.offset]
                
                # Si hay una nota en la misma posición que el silencio, eliminar el silencio
                if overlapping_notes:
                    part.remove(overlapping_notes)
                    part.remove(element)

    return score

def convert_midi_to_pdf(midi_path, output_folder):
    # Limpiar el archivo MIDI de silencios innecesarios
    cleaned_score = clean_midi(midi_path)

    # Guardar la partitura como PDF usando LilyPond
    # pdf_filename = os.path.join(output_folder, os.path.basename(midi_path).replace('.mid', '.pdf'))
    # cleaned_score.write('lily.pdf', fp=pdf_filename)
    # Convertir a MusicXML
    score = converter.parse(cleaned_score)
            
    # Aplicar algunas optimizaciones para mejorar la legibilidad
    score.makeNotation(inPlace=True)
            
    # Guardar como MusicXML
    xml_path = os.path.join(output_folder, "score.musicxml")
    score.write('musicxml', fp=xml_path)
    return score

convert_midi_to_pdf("output.mid", "./")
# def inspect_and_convert_midi_to_pdf(midi_path, output_dir):
#     try:
#         score = converter.parse(midi_path)
#         print("Partitura analizada correctamente. Inspeccionando elementos...")
#         for part in score.parts:
#             print(f"Parte: {part.id}")
#             for element in part.flat.notesAndRests:
#                 print(f"Elemento: {element}, Duración: {element.quarterLength}")
        
#         pdf_path = os.path.join(output_dir, os.path.basename(midi_path).replace(".mid", ".pdf"))
#         score.write('musicxml.pdf', fp=pdf_path)
#         return pdf_path

#     except Exception as e:
#         print(f"Error al analizar el archivo MIDI: {e}")
#         raise

# # Uso:
# inspect_and_convert_midi_to_pdf("archivo_limpio.mid", "./")

# import subprocess

# def convert_midi_to_pdf_with_musescore(midi_path, output_dir, musescore_path="musescoreDirectPNGPath"):
#     pdf_path = os.path.join(output_dir, os.path.basename(midi_path).replace(".mid", ".pdf"))
#     subprocess.run([musescore_path, midi_path, "-o", pdf_path], check=True)
#     return pdf_path

# # Uso:
# pdf_path = convert_midi_to_pdf_with_musescore("archivo_limpio.mid", "./")
# print(f"Archivo PDF generado en: {pdf_path}")