def leer_archivo(archivo):
    import pandas as pd
    import json
    """
    Función que procesa:
    - Archivos .txt (con formato médico específico)
    - Archivos .csv 
    - Archivos .json
    
    Devuelve siempre una lista de diccionarios con los datos estructurados.
    """
    try:
        # Procesamiento para archivos TXT (usando tu lógica específica)
        if archivo.endswith('.txt'):
            with open(archivo, 'r', encoding='utf-8') as file:
                lines = [line.strip() for line in file.readlines() if line.strip()]

            # Filtrar líneas relevantes según el patrón esperado
            filtered_lines = [
                line for line in lines 
                if line.startswith("3O|") or line.startswith("4R|1|") or 
                   line.startswith("6R|3|") or line.startswith("0R|5|") or
                   line.startswith("2R|7|") or line.startswith("4R|9|") or
                   line.startswith("6R|11|") or line.startswith("1H|")
            ]

            # Extraer datos según posiciones fijas
            try:
                parsed_data = {
                    "id": filtered_lines[1].split('|')[2],
                    "age": filtered_lines[1].split('|')[4].split('^')[3],
                    "name": filtered_lines[1].split('|')[12],
                    "last_name": filtered_lines[1].split('|')[13],
                    "gender": filtered_lines[1].split('|')[-1].strip(),
                    "date": filtered_lines[0].split('|')[-1].strip()[:10],
                    "A1b_Area": float(filtered_lines[2].split('|')[3]),
                    "F_Area": float(filtered_lines[3].split('|')[3]),
                    "A1c_Area": float(filtered_lines[4].split('|')[3]),
                    "P3_Area": float(filtered_lines[5].split('|')[3]),
                    "A0_Area": float(filtered_lines[6].split('|')[3]),
                    "S_Window_Area": float(filtered_lines[7].split('|')[3])
                }
                return [parsed_data]  # Convertir a lista para consistencia
            except IndexError as e:
                raise ValueError(f"El archivo TXT no tiene el formato esperado: {str(e)}")

        # Procesamiento para archivos CSV
        elif archivo.endswith('.csv'):
            df = pd.read_csv(archivo, sep=None, engine='python', encoding='utf-8', dtype=str)
            df.columns = [col.strip() for col in df.columns]  # Limpiar nombres de columnas
            df = df.where(pd.notnull(df), None)  # Convertir NaN a None
            return df.to_dict('records')  # Convertir DataFrame a lista de diccionarios

        # Procesamiento para archivos JSON
        elif archivo.endswith('.json'):
            with open(archivo, 'r', encoding='utf-8') as f:
                datos = json.load(f)
                return [datos] if isinstance(datos, dict) else datos

        else:
            raise ValueError("Formato de archivo no soportado. Use .txt, .csv o .json")

    except Exception as e:
        print(f"Error al procesar {archivo}: {str(e)}")
        return []
    
def subir_a_mongo(datos, coleccion, campo_clave="id"):
    """
    Sube datos a MongoDB verificando primero si ya existen.
    
    datos (list): Lista de diccionarios con los datos a subir
    coleccion (pymongo.collection): Colección de MongoDB
    campo_clave (str): Campo único para verificar duplicados
        
    Devuelve: (cantidad_insertados, duplicados_encontrados)
    """
    if not datos:
        print("No hay datos para subir")
        return 0, 0
        
    insertados = 0
    duplicados = 0
    
    for registro in datos:
        # Verificar si el registro ya existe (usando el campo_clave)
        if campo_clave in registro and registro[campo_clave]:
            existe = coleccion.find_one({campo_clave: registro[campo_clave]})
            
            if existe:
                print(f"Registro con {campo_clave} {registro[campo_clave]} ya existe en MongoDB")
                duplicados += 1
                continue
                
        # Insertar el registro si no existe
        try:
            coleccion.insert_one(registro)
            insertados += 1
        except Exception as e:
            print(f"Error al insertar registro: {str(e)}")
            
    print(f"\nResumen:")
    print(f"- Registros insertados: {insertados}")
    print(f"- Registros duplicados: {duplicados}")
    
    return insertados, duplicados

def buscar(coleccion, id_paciente):
    """Busca y devuelve la información de un paciente por id."""
    paciente = coleccion.find_one({"id": id_paciente})
    if paciente:
        paciente.pop('_id', None)  # quitar el _id
        print(f"Paciente encontrado: {paciente}")
        return paciente
    else:
        print(f"No se encontró paciente con id {id_paciente}")
        return None
    
def crear_o_agregar(coleccion, id_paciente, nuevos_datos):
    """
    Crea un paciente nuevo o agrega datos a uno existente.
    nuevos_datos debe ser un diccionario con los campos a agregar o actualizar.
    Ejemplo: {"name": "Nuevo Nombre", "age": 30}
    """
    paciente = coleccion.find_one({"id": id_paciente})
    
    if paciente:
        # El paciente existe, agregamos o actualizamos los datos
        resultado = coleccion.update_one(
            {"id": id_paciente},
            {"$set": nuevos_datos}
        )
        print(f"Datos agregados o actualizados para paciente con id {id_paciente}")
        return resultado.modified_count
    else:
        # El paciente no existe, lo creamos
        nuevos_datos["id"] = id_paciente
        resultado = coleccion.insert_one(nuevos_datos)
        print(f"Paciente creado con id {id_paciente}")
        return resultado.inserted_id

def actualizar(coleccion, id_actual, nuevos_datos):
    """
    Actualiza la información de un paciente.
    Permite cambiar el mismo id también.
    nuevos_datos debe ser un diccionario con los campos a actualizar.
    Ejemplo: {"id": "1234","name": "Nuevo Nombre", "age": 30}
    """
    paciente = coleccion.find_one({"id": id_actual})
    if paciente:
        resultado = coleccion.update_one(
            {"id": id_actual},
            {"$set": nuevos_datos}
        )
        print(f"Paciente actualizado")
        return resultado.modified_count
    else:
        print(f"No se encontró paciente con id {id_actual}")
        return 0

def eliminar(coleccion, id_paciente):
    """Elimina un paciente por id."""
    resultado = coleccion.delete_one({"id": id_paciente})
    if resultado.deleted_count:
        print(f"Paciente con id {id_paciente} eliminado")
    else:
        print(f"No se encontró paciente con id {id_paciente}")
    return resultado.deleted_count