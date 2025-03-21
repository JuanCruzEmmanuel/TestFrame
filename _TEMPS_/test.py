import json

with open("_TEMPS_/protocolo_a_ejecutar.json", "r") as file:
    datos = json.load(file)
pasos=0
for bloque in datos:
    pasos+=len(bloque["Pasos"])

print(pasos)