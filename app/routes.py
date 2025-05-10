from flask import render_template, Blueprint, request, redirect, url_for, send_file, flash
from .utils.download import download_audio
from .utils.preprocess import convert_to_wav
from .utils.generate_score import convert_midi_to_pdf_with_musescore
from .utils.clean import clean_midi
import os
import traceback

main = Blueprint('main', __name__)

# Directorios de archivos
UPLOAD_FOLDER = 'uploads/'
OUTPUT_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'output/')
MIDI_FOLDER = os.path.join(OUTPUT_FOLDER, 'midi/')
PDF_FOLDER = os.path.join(OUTPUT_FOLDER, 'pdf/')

# Asegurar que las carpetas existen
for model in ['onsets_and_frames', 'basic_pitch', 'transkun']:
    os.makedirs(os.path.join(MIDI_FOLDER, model), exist_ok=True)
    os.makedirs(os.path.join(PDF_FOLDER, model), exist_ok=True)

@main.route("/")
def index():
    return render_template("index.html")

@main.route('/transcribir', methods=['POST'])
def transcribir():
    try:
        audio_path = ""
        youtube_url = request.form.get('youtube_url', '').strip()
        audio = request.files.get('audio_file')

        # Validación: Ambos campos llenos
        if youtube_url and audio and audio.filename:
            flash("Solo puedes proporcionar un enlace de YouTube o un archivo, no ambos.", "error")
            return redirect(url_for("main.index"))

        # Validación: Ninguno de los campos está lleno
        if not youtube_url and (not audio or audio.filename == ''):
            flash("No se proporcionó un archivo ni un enlace de YouTube.", "error")
            return redirect(url_for("main.index"))

        # Validación: Archivo cargado pero en formato incorrecto
        if audio and audio.filename:
            if not (audio.filename.lower().endswith('.mp3') or audio.filename.lower().endswith('.wav')):
                flash("Formato de archivo no válido. Solo se permiten MP3 y WAV.", "error")
                return redirect(url_for("main.index"))

            audio_path = os.path.join(UPLOAD_FOLDER, audio.filename)
            audio.save(audio_path)

        # Validación: Enlace de YouTube
        if youtube_url:
            try:
                audio_path = download_audio(youtube_url)
                if not audio_path:
                    raise Exception("No se pudo obtener el audio del enlace proporcionado.")
            except Exception as e:
                flash(f"Error al descargar el audio de YouTube: {str(e)}", "error")
                print(traceback.format_exc())
                return redirect(url_for("main.index"))

        # Convertir a WAV
        try:
            wav_path = convert_to_wav(audio_path)
        except Exception as e:
            flash(f"Error al convertir el archivo a WAV: {str(e)}", "error")
            print(traceback.format_exc())
            return redirect(url_for("main.index"))

        # Obtener el modelo seleccionado
        selected_model = request.form.get('model', 'maestro')

        midi_output_folder = os.path.join(MIDI_FOLDER, selected_model)
        pdf_output_folder = os.path.join(PDF_FOLDER, selected_model)

        # Realizar la transcripción según el modelo seleccionado
        try:
            if selected_model == 'onsets_and_frames':
                from .models.transcription_onsets import transcribe_with_onsets_and_frames
                midi_path = transcribe_with_onsets_and_frames(wav_path, midi_output_folder)
            elif selected_model == 'basic_pitch':
                from .models.transcription_basic import transcribe_with_basic_pitch
                midi_path = transcribe_with_basic_pitch(wav_path, midi_output_folder)
            elif selected_model == 'transkun':
                from .models.transcription_transkun import transcribe_with_transkun
                midi_path = transcribe_with_transkun(wav_path, midi_output_folder)
            else:
                flash("Modelo de transcripción no válido.", "error")
                return redirect(url_for("main.index"))

        except Exception as e:
            flash(f"Error durante la transcripción: {str(e)}", "error")
            print(traceback.format_exc())
            return redirect(url_for("main.index"))

        flash("Proceso finalizado con éxito", "success")
        # Generación de la partitura PDF
        try:
            pdf_path = convert_midi_to_pdf_with_musescore(midi_path, pdf_output_folder)
        except Exception as e:
            flash(f"Error al generar la partitura: {str(e)}", "error")
            print(traceback.format_exc())
            return redirect(url_for("main.index"))

        return render_template('index.html', model=selected_model, midi_file=os.path.basename(midi_path), pdf_file=os.path.basename(pdf_path))

    except Exception as e:
        flash(f"Error general en la transcripción: {str(e)}", "error")
        print(traceback.format_exc())
        return redirect(url_for("main.index"))

@main.route('/download/<model>/<filename>')
def download_file(model, filename):
    try:
        path = os.path.join(MIDI_FOLDER, model, filename)
        return send_file(path, as_attachment=True)
    except Exception as e:
        flash(f"Error al descargar el archivo: {str(e)}", "error")
        return redirect(url_for("main.index"))

@main.route('/view_pdf/<model>/<filename>')
def view_pdf(model, filename):
    try:
        path = os.path.join(PDF_FOLDER, model, filename)
        return send_file(path)
    except Exception as e:
        flash(f"Error al visualizar el PDF: {str(e)}", "error")
        return redirect(url_for("main.index"))
