# app.py
from flask import Flask, render_template, Blueprint, request,redirect, url_for, send_file
from .utils.download import download_audio
from .utils.preprocess import convert_to_wav
from .utils.generate_score import convert_midi_to_pdf_with_musescore
from .utils.clean import clean_midi
import os

main = Blueprint('main', __name__)

# Directorios de archivos
UPLOAD_FOLDER = 'uploads/'
MIDI_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'midi/') 
PDF_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'pdf/')

@main.route("/")
def index():
    return render_template("index.html")


@main.route('/transcribir', methods=['POST'])
def transcribir():
    audio_path=""
    if 'audio_file' in request.files and request.files['audio_file'].filename != '':
        audio = request.files['audio_file']
        audio_path = os.path.join(UPLOAD_FOLDER, audio.filename)
        audio.save(audio_path)
        

    elif 'youtube_url' in request.form and request.form['youtube_url'].strip() != '':
        url = request.form['youtube_url']
        audio_path = download_audio(url)

    # Convertir el MP3 descargado a WAV
    if audio_path.endswith('.mp3') or audio_path.endswith('.wav'):
        wav_path = convert_to_wav(audio_path)
    else:
        return "Error al descargar el archivo de YouTube", 500
    
     # Obtener el modelo seleccionado
    selected_model = request.form.get('model', 'maestro')

    # Realizar la transcripción según el modelo seleccionado
    try:
        if selected_model == 'onsets_and_frames':
            from .utils.transcribe_v import transcribe_with_onsets_and_frames
            midi_path = transcribe_with_onsets_and_frames(wav_path, MIDI_FOLDER)
        elif selected_model == 'basic_pitch':
            from .utils.basic import transcribe_with_basic_pitch
            print("entro")
            midi_path = transcribe_with_basic_pitch(wav_path, MIDI_FOLDER)
        else:
            return "Modelo no válido seleccionado", 400
    except Exception as e:
        return f"Error durante la transcripción: {str(e)}", 500   

     # Redirigir al formulario inicial con el enlace al archivo MIDI, si existe
    if midi_path:
         # Limpiar MIDI antes de la conversión
        cleaned_midi_path = clean_midi(midi_path)
        pdf_path = convert_midi_to_pdf_with_musescore(cleaned_midi_path, PDF_FOLDER)
        return render_template('index.html', midi_file=os.path.basename(cleaned_midi_path), pdf_file=os.path.basename(pdf_path))
    else:
        return redirect(url_for("main.index"))
    

@main.route('/download/<filename>')
def download_file(filename):
    path = os.path.join(MIDI_FOLDER,filename)
    return send_file(path, as_attachment=True)

@main.route('/view_pdf/<filename>')
def view_pdf(filename):
    path = os.path.join(PDF_FOLDER, filename)
    return send_file(path)