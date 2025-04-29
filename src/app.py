from flask import Flask, jsonify, render_template, request, redirect, url_for, flash
from SistemaHospitalario import paciente
from conexion import coleccion_pacientes
from funciones import eliminar, leer_archivo, subir_a_mongo
from werkzeug.utils import secure_filename
import os

template_dir = os.path.join(os.path.dirname(__file__), 'templates')
ALLOWED_EXTENSIONS = {'txt', 'csv', 'json'}
UPLOAD_FOLDER = 'data'
app = Flask(__name__)
app.secret_key = 'supersecretkey'  # Necesario para usar flash
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
@app.route('/')
def inicio():
    
    return render_template('index.html')  

@app.route('/users')
def usersHandler():
    return jsonify({"pacientes":paciente()})

@app.route('/delete', methods=['GET', 'POST'])
def delete_patient():
    if request.method == 'POST':
        # Obtenemos el id desde el formulario
        id_paciente = request.form['id']
        
        # Llamamos a la función eliminar para borrar el paciente
        result = eliminar(coleccion_pacientes, id_paciente)
        
        if result:
            # Si el paciente fue eliminado, mostramos un mensaje de éxito
            flash("Paciente eliminado exitosamente!", "success")
        else:
            # Si no se encontró al paciente, mostramos un mensaje de error
            flash("Paciente no encontrado.", "danger")

    # Si es un GET (cuando se accede directamente a la página), simplemente mostramos el formulario
    return render_template('delete.html')
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/add', methods=['GET', 'POST'])
def add_patient():
    if request.method == 'POST':
        if 'id' not in request.files:
            flash("❌ No se seleccionó ningún archivo.", "danger")
            return render_template('add.html')

        archivo = request.files['id']
        if archivo.filename == '':
            flash("⚠️ Nombre de archivo vacío. Selecciona un archivo válido.", "warning")
            return render_template('add.html')

        if not allowed_file(archivo.filename):
            flash("⚠️ Tipo de archivo no permitido. Solo .txt, .csv o .json.", "warning")
            return render_template('add.html')

        filename = secure_filename(archivo.filename)
        ruta = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        # 🔐 Asegúrate de que el directorio exista
        os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

        # ✅ Guardar archivo antes de procesar
        archivo.save(ruta)

        result = leer_archivo(ruta)

        if not result:
            os.remove(ruta)  # Limpieza solo si el archivo no es válido
            flash("❌ No se cargó el archivo. Revisa el formato o contenido.", "danger")
        else:
            flash("✅ Archivo cargado correctamente.", "success")

    return render_template('add.html')


 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
