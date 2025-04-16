"""
Va a controlar las variables
"""

import sympy as sp
import json

def tiene_decimales(numero):

    """
    Por una cuestion de uso en el SMVA, es necesario saber distinguir entre int y float por si se necesitan setear banderas. Se crea esta funcion que evalua si el numero es entero o no

    si el numero por ejemplo es 1.0, numericamente es igual a 1; entonces el resultado es un True, en caso contrario es False

    1.0 = 1 ----> True
    1.1 = 1 ----> False

    El int(num) convierte cualquier numero en su entero, sin redondearlo es decir int(1.9)=1
    """
    return numero !=int(numero)

def evaluar_expresion(expresion, variables):

    """
    Esta funcion recibe la expresion matematica y el diccionario de variables.
    Primero reemplaza cada elemento de la expresion que aparece en el diccionario. Utilizando el metodo .replace
    Luego convierte el resultado de resolver la expresion en un float. Para luego evaluar si su valor se puede considerar entero (En terminos practicos, un valor entero solo lo vamos a tener si nosotros forzamos a ese valor
    ya que en la practica es casi imposible una medicion sin decimales; por eso vi la necesidad de agregar esa instruccion de convertir en entero por si necesitamos alguna bandera)
    """
    # Reemplazar las variables por sus valores correspondientes
    for var, valor in variables.items():
        expresion = expresion.replace(var, str(valor))
    
    try:
        # Evaluar la expresión utilizando sympy
        resultado = float(sp.sympify(expresion))

    except Exception as e:
        return f"Error al evaluar la expresión: {e}"
    
    if tiene_decimales(resultado):
        pass
    else:
        resultado=int(resultado)
        
    return resultado

def leer_variables_desde_json():

    """
    Funcion en cargada de leer el json de las variables. Esta lo que hace en resumen es convertir los valores en un diccionario facil de trabajar desde python
    supongamos un json:
    {
    var1 = 1;
    var2 = 3;
    }
    """
    with open(r"_TEMPS_\variables.json","r") as file:
        VARIABLES = json.load(file)
    
    return VARIABLES


def equation(CMD):
    """
    Esta es la funcion que llama el SMVA, es decir la funcion "main". 
    La funcion recibe la expresion que se quiere evaluar pj. (2*x-1); luego analiza todas las variables que se encuentre en el xml y lo convierte en diccionario.
    Por ultimo en evaluar_expresion cambia el valor de la variable, por su valor en el diccionario y la evalua numericamente.

    pj. 
    2*x-1

    diccionario = {x:10, y:1, z:5.5,........,xn=n}
    diccionario(x)=10.0 (por una cuestion de facilidad, converti todo a float)
    2*10-1 = 19.0

    resultado = 19 (ya que pasa por la funcion preguntando si el valor es un entero o no; luego el smva se encarga solo en convertirlo en double cuando se especifica que es una medicion)
    """
    variables = leer_variables_desde_json()

    resultado = evaluar_expresion(CMD, variables)

    return resultado