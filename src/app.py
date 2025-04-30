from flask import Flask, jsonify, render_template, request, redirect, url_for, flash, make_response
from SistemaHospitalario import paciente
from conexion import coleccion_pacientes
from funciones import eliminar, leer_archivo, subir_a_mongo, buscar
from werkzeug.utils import secure_filename
from datetime import datetime
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


@app.route('/users', methods=['GET', 'POST'])
def usersHandler():
    sujeto = None

    if request.method == 'POST':
        id_paciente = request.form.get('id')
        sujeto = buscar(coleccion_pacientes, str(id_paciente))
        if not sujeto:
            flash("❌ Paciente no encontrado.", "danger")

    elif request.method == 'GET' and request.args.get('descargar'):
        id_paciente = request.args.get('id')
        sujeto = buscar(coleccion_pacientes, str(id_paciente))
        if not sujeto:
            flash("❌ Paciente no encontrado para descarga.", "danger")
            return redirect('/users')

        # Generar mensaje HL7 según los datos del paciente
        now = datetime.now().strftime("%Y%m%d%H%M%S")
        
        msh = f"MSH|^~\\&|APP|CLINIC|SYSTEM|RECEIVER|{now}||ORU^R01|{id_paciente}|P|2.3"
        pid = f"PID|1||{sujeto.get('id', '')}||{sujeto.get('last_name', '')}^{sujeto.get('name', '')}||{sujeto.get('date', '')}|{sujeto.get('gender', '')}"
        obx_list = []

        # Agregar OBX para cada medición si existe
        for i, key in enumerate(['A1b_Area', 'F_Area', 'A1c_Area', 'P3_Area', 'A0_Area', 'S_Window_Area'], start=1):
            if key in sujeto:
                obx_list.append(f"OBX|{i}|NM|{key}||{sujeto[key]}|u.a.|N|||F")

        hl7_message = "\n".join([msh, pid] + obx_list)

        response = make_response(hl7_message)
        response.headers["Content-Disposition"] = f"attachment; filename=paciente_{id_paciente}.hl7"
        response.headers["Content-Type"] = "text/plain"
        return response

    return render_template('users.html', sujeto=sujeto)



@app.route('/delete', methods=['GET', 'POST'])
def delete_patient():
    if request.method == 'POST':
        # Obtenemos el id desde el formulario
        id_paciente = request.form['id']
        
        # Llamamos a la función eliminar para borrar el paciente
        result = eliminar(coleccion_pacientes, str(id_paciente))
        
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

        archivo.save(ruta)

        result = leer_archivo(ruta)

        if not result:
            os.remove(ruta)  # Limpieza solo si el archivo no es válido
            flash("❌ No se cargó el archivo. Revisa el formato o contenido.", "danger")
        else:
            insertados, duplicados = subir_a_mongo(result, coleccion_pacientes, "id")

            if duplicados > 0:
                flash("❌ Archivo con ID ya existente. No se cargó.", "danger")
                os.remove(ruta)
            elif insertados > 0:
                flash("✅ Archivo cargado correctamente.", "success")
            else:
                flash("❌ Archivo con formato inválido o sin datos.", "danger")
            

    return render_template('add.html')

@app.route('/update', methods=['GET', 'POST'])
def update():
    return render_template('update.html')
 
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)
