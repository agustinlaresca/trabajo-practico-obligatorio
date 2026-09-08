import re
from functools import reduce

#   TOURNEYMANAGER - Sistema de Gestion de Torneos
# Matrices principales (listas bidimensionales):
#
#   jugadores[i] = [codigo, nombre, gamertag, email, codigo_equipo]
#     [0] codigo        -> JUG-XXXX
#     [1] nombre        -> nombre completo
#     [2] gamertag      -> nombre de usuario
#     [3] email         -> email de contacto
#     [4] codigo_equipo -> equipo asignado (vacio si no tiene)
#
#   equipos[i] = [codigo, nombre]
#     [0] codigo -> EQ-XXX
#     [1] nombre -> nombre del equipo
#
#   partidas[i] = [codigo_eq1, codigo_eq2, ganador, fase]
#     [0] codigo_eq1 -> equipo local
#     [1] codigo_eq2 -> equipo visitante
#     [2] ganador    -> codigo del ganador o "EMPATE"
#     [3] fase       -> "Grupos", "Semifinal" o "Final"

jugadores = []
equipos   = []
partidas  = []


# FUNCIONES DE VALIDACION - EXPRESIONES REGULARES

def validar_codigo_jugador(codigo):
    # valida que el codigo tenga formato JUG-XXXX (4 digitos)
    if re.match(r'^JUG-\d{4}$', codigo):
        return True
    else:
        return False

def validar_codigo_equipo(codigo):
    # valida que el codigo tenga formato EQ-XXX (3 digitos)
    if re.match(r'^EQ-\d{3}$', codigo):
        return True
    else:
        return False

def validar_email(email):
    # valida el formato del email con expresión regular
    if re.match(r'^[\w\.]+@[\w]+\.[a-z]{2,}$', email):
        return True
    else:
        return False

def extraer_numero_codigo(codigo):
    # extrae la parte numérica de un código usando findall
    # ej: JUG-0012 -> '0012'
    resultado = re.findall(r'\d+', codigo)
    if len(resultado) > 0:
        return resultado[0]
    return ""

def enmascarar_email(email):
    # oculta el usuario del email usando re.sub
    # ejemplo: usuario@mail.com -> XXXX@mail.com
    resultado = re.sub(r'^[A-Za-z0-9._%+-]+', 'XXXX', email)

    return resultado
