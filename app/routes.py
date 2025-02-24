# app.py
from flask import Flask, render_template, Blueprint, request,redirect, url_for, send_file, flash
from .utils.download import download_audio
from .utils.preprocess import convert_to_wav
from .utils.generate_score import convert_midi_to_pdf_with_musescore
from .utils.clean import clean_midi
import os
import traceback

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
    try:
        audio_path=""
        if 'audio_file' in request.files and request.files['audio_file'].filename != '':
            audio = request.files['audio_file']
            audio_path = os.path.join(UPLOAD_FOLDER, audio.filename)
            audio.save(audio_path)
            flash(f"Archivo {audio.filename} subido correctamente.", "success")

        elif 'youtube_url' in request.form and request.form['youtube_url'].strip() != '':
            url = request.form['youtube_url']
            audio_path = download_audio(url)
            flash(f"Descarga desde YouTube completada: {audio_path}", "success")
        
        else:
            flash("No se proporcionó un archivo ni un enlace de YouTube.", "error")
            return redirect(url_for("main.index"))
        
        # Convertir el MP3 descargado a WAV
        if audio_path.endswith('.mp3') or audio_path.endswith('.wav'):
            wav_path = convert_to_wav(audio_path)
            flash(f"Conversión a WAV completada: {wav_path}", "success")
        else:
            flash("Error al descargar el archivo de YouTube.", "error")
            return redirect(url_for("main.index"))
        
        # Obtener el modelo seleccionado
        selected_model = request.form.get('model', 'maestro')

        # Realizar la transcripción según el modelo seleccionado
        try:
            if selected_model == 'onsets_and_frames':
                from .models.transcribe_v import transcribe_with_onsets_and_frames
                midi_path = transcribe_with_onsets_and_frames(wav_path, MIDI_FOLDER)
            elif selected_model == 'basic_pitch':
                from .models.basic import transcribe_with_basic_pitch
                midi_path = transcribe_with_basic_pitch(wav_path, MIDI_FOLDER)
            elif selected_model == 'transkun':
                from .models.transkun import transcribe_with_transkun
                midi_path = transcribe_with_transkun(wav_path, MIDI_FOLDER)
            else:
                flash("Modelo de transcripción no válido.", "error")
                return redirect(url_for("main.index"))
            
            flash(f"Transcripción completada: {midi_path}", "success")
        except Exception as e:
                flash(f"Error durante la transcripción: {str(e)}", "error")
                print(traceback.format_exc())  # Mostrar detalles del error en la consola
                return redirect(url_for("main.index"))  

        # Redirigir al formulario inicial con el enlace al archivo MIDI, si existe
        try:
            # Limpiar MIDI antes de la conversión
            # cleaned_midi_path = clean_midi(midi_path)
            pdf_path = convert_midi_to_pdf_with_musescore(midi_path, PDF_FOLDER)
            flash(f"Partitura generada: {pdf_path}", "success")
        except Exception as e:
                flash(f"Error al generar la partitura: {str(e)}", "error")
                print(traceback.format_exc())
                return redirect(url_for("main.index"))
        return render_template('index.html', midi_file=os.path.basename(midi_path), pdf_file=os.path.basename(pdf_path))

    except Exception as e:
        flash(f"Error general en la transcripción: {str(e)}", "error")
        print(traceback.format_exc())
        return redirect(url_for("main.index"))

@main.route('/download/<filename>')
def download_file(filename):
    try:
        path = os.path.join(MIDI_FOLDER, filename)
        return send_file(path, as_attachment=True)
    except Exception as e:
        flash(f"Error al descargar el archivo: {str(e)}", "error")
        return redirect(url_for("main.index"))


@main.route('/view_pdf/<filename>')
def view_pdf(filename):
    try:
        path = os.path.join(PDF_FOLDER, filename)
        return send_file(path)
    except Exception as e:
        flash(f"Error al visualizar el PDF: {str(e)}", "error")
        return redirect(url_for("main.index"))