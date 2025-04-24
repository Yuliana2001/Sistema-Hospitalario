from funciones import *
from conexion import coleccion_pacientes
import os
# Diseñe una aplicación en Python o su lenguaje de preferencia, que simule la recepción de
# archivos de comunicación de Dispositivos Médicos en protocolos Serial, csv y json, dichos
# archivos deben ser procesados, es decir, extraer la información útil de estos, la cual será
# enviada al servidor Mongodb Atlas que cada grupo configurará.
contentJson= leer_archivo('src/paciente1.json')
contentCsv= leer_archivo('src/paciente2.csv')
contentTxt= leer_archivo('src/paciente3.txt')

# Extraer las claves (columnas) del CSV
listaCsvItems = list(contentCsv[0].keys())  # Asumimos que contentCsv no está vacío
nombreColumna = listaCsvItems

# Extraer las celdas de cada fila
listaCsvCelda = [list(fila.values()) for fila in contentCsv]


listaPacientes =[]
listaPacientes.extend([contentCsv[0],contentJson[0]])
print(listaPacientes)
if listaPacientes:
    coleccion_pacientes.insert_many(listaPacientes)
    print("Pacientes insertados correctamente.")
else:
    print("No hay pacientes para insertar.")#mandar a la base de datos

# La aplicación también deberá contar con una sección que permita hacer un CRUD a la base
# de datos no relacional. El campo del documento con el cual se harán los query es el número
# de identificación (ID), es decir, para buscar, actualizar o eliminar pacientes de la base de
# datos, se debe hacer buscando a través del número del documento de identidad. Esto quiere
# decir que el único campo que será obligatoria es este ID. Recuerden que una cosa es el “_id”:
# campo de las bases de datos no relacionales y otro es el ID: documento de identidad del
# paciente.