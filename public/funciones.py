def leer_archivo(archivo):
    import csv
    import json
    if archivo.endswith(".csv"):
        # Abrimos el archivo CSV con el delimitador adecuado
        with open(archivo, encoding='utf-8') as file:
            contentCsv = csv.DictReader(file, delimiter=';', quotechar='"')
            return list(contentCsv)

    elif archivo.endswith(".json"):
        with open(archivo) as json_file:
            content = json.load(json_file)
            return content

    elif archivo.endswith(".txt"):
        with open(archivo, 'r') as text_file:
            content = text_file.read()
            return content

