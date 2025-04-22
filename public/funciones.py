def leer_archivo(archivo):
    import csv
    import json
    if archivo.endswith(".csv"):
        file = open(archivo , encoding='utf-8')
        content = csv.reader(file , delimiter=',')
        for row in content:
            j+=1
            print(row)
        file.close()
    elif archivo.endswith(".json"):
        with open(archivo) as json_file:
            data = json.load(json_file)
            print(data)
    elif archivo.endswith(".text"):
        with open(archivo, 'r') as text_file:
            content = text_file.read()