from funciones import *
from conexion import coleccion_pacientes, client, db
import os
# Diseñe una aplicación en Python o su lenguaje de preferencia, que simule la recepción de
# archivos de comunicación de Dispositivos Médicos en protocolos Serial, csv y json, dichos
# archivos deben ser procesados, es decir, extraer la información útil de estos, la cual será
# enviada al servidor Mongodb Atlas que cada grupo configurará.

# Procesar archivos
archivos = [
    'src/data/paciente1.json',
    'src/data/paciente2.csv',
    'src/data/paciente3.txt'
]

for archivo in archivos:
    if not os.path.exists(archivo):
        print(f"Archivo {archivo} no encontrado")
        continue
        
    print(f"\nProcesando {archivo}...")
    datos = leer_archivo(archivo)
    
    if datos:
        # Subir a MongoDB verificando duplicados por "id" (ajusta según tu estructura)
        subir_a_mongo(datos, coleccion_pacientes, campo_clave="id")
    else:
        print("No se pudieron obtener datos del archivo")
        
# Mostrar documentos en la colección Paciente
print("\nDocumentos en Paciente:")
def paciente():
    pacientes = list(coleccion_pacientes.find())
    for p in pacientes:
        p["_id"] = str(p["_id"])  # Convierte ObjectId a string
    return pacientes

# La aplicación también deberá contar con una sección que permita hacer un CRUD a la base
# de datos no relacional. El campo del documento con el cual se harán los query es el número
# de identificación (ID), es decir, para buscar, actualizar o eliminar pacientes de la base de
# datos, se debe hacer buscando a través del número del documento de identidad. Esto quiere
# decir que el único campo que será obligatoria es este ID. Recuerden que una cosa es el “_id”:
# campo de las bases de datos no relacionales y otro es el ID: documento de identidad del
# paciente.