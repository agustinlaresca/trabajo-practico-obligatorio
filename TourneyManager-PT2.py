"""
TourneyManager - Segunda entrega
Sistema de gestión de torneos de videojuegos.

Permite registrar jugadores y equipos, inscribir jugadores,
registrar partidas, modificar información y consultar resultados.

Los datos del torneo se guardan automáticamente en torneo.json
y se recuperan al iniciar nuevamente el programa.

También permite generar, leer, actualizar y eliminar un reporte
de texto llamado reporte_torneo.txt.
"""
import json
import re
import os
from functools import reduce

# ========================================================================
# ESTRUCTURAS Y BÚSQUEDAS
# ========================================================================

def crear_datos():
    """Cada llamada crea matrices nuevas, agrupadas en un diccionario."""
    return {"jugadores": [], "equipos": [], "partidas": []}


def buscar_por_codigo(matriz, codigo):
    """Búsqueda secuencial; devuelve índice o -1."""
    for i in range(len(matriz)):
        if matriz[i][0] == codigo:
            return i
    return -1


def buscar_jugador_por_codigo(jugadores, codigo):
    """Busca un jugador utilizando su código identificador."""
    return buscar_por_codigo(jugadores, codigo)


def buscar_equipo_por_codigo(equipos, codigo):
    """Busca un equipo utilizando su código identificador."""
    return buscar_por_codigo(equipos, codigo)


def obtener_codigos(matriz):
    """Set de identificadores: útil para duplicados y pertenencia."""
    return set(map(lambda fila: fila[0], matriz))


def nombre_equipo(equipos, codigo):
    """Obtiene el nombre de un equipo a partir de su código."""
    indice = buscar_equipo_por_codigo(equipos, codigo)
    if indice == -1:
        return "Sin equipo"
    return equipos[indice][1]


def clave_partida(codigo1, codigo2, fase):
    """Tupla que identifica un cruce por fase, sin importar el orden rival/local."""
    if codigo1 < codigo2:
        return (codigo1, codigo2, fase)
    return (codigo2, codigo1, fase)

# ========================================================================
# VALIDACIONES
# ========================================================================

# Tupla: las fases disponibles no cambian durante la ejecución.
FASES = ("Grupos", "Semifinal", "Final")


def normalizar_codigo(codigo):
    """Devuelve un código sin espacios exteriores y en mayúsculas."""
    return codigo.strip().upper()

def validar_codigo_jugador(codigo):
    """
    Valida el código ingresado por el usuario.
    Es decir que el código tenga formato JUG-XXXX (4 dígitos)
    """
    if re.match(r'^JUG-\d{4}$', codigo) and codigo != "JUG-0000":
        return True
    else:
        return False

def validar_codigo_equipo(codigo):
    """
    Valida que el código ingresado por usuario.
    Asegura que el código tenga formato EQ-XXX (3 digitos)
    """
    if re.match(r'^EQ-\d{3}$', codigo) and codigo != "EQ-000":
        return True
    else:
        return False

def validar_email(email):
    """
    Valida el formato del email con expresión regular
    Se asegura que tenga el formato clásico de nombre@dominio.extensión
    """
    if re.match(r'^[\w\.]+@[\w]+\.[a-z]{2,}$', email):
        return True
    else:
        return False
    
def validar_texto(texto, campo, maximo=60):
    """Verifica que un texto no esté vacío ni supere el máximo."""
    texto = texto.strip()

    if len(texto) == 0:
        raise ValueError(campo + " no puede estar vacío.")

    if len(texto) > maximo:
        raise ValueError(campo + " no puede superar los " + str(maximo) + " caracteres.")

    return texto

def convertir_opcion(texto, minimo, maximo):
    """Convierte una opción del menú a entero y verifica su rango."""
    numero = int(texto)

    if numero < minimo or numero > maximo:
        raise ValueError("Opción fuera de rango.")

    return numero

def obtener_fase(opcion):
    numero = convertir_opcion(opcion, 1, len(FASES))
    return FASES[numero - 1]

def extraer_numero_codigo(codigo):
    """
    Extrae la parte numérica de un código usando findall
    ej: JUG-0012 -> '0012'
    """
    resultado = re.findall(r'\d+', codigo)
    if len(resultado) > 0:
        return resultado[0]
    return ""

def enmascarar_email(email):
    """
    Oculta el usuario del email usando re.sub.
    Ej: usuario@mail.com -> XXXX@mail.com
    """
    resultado = re.sub(r'^[^@]+', 'XXXX', email)
    return resultado

# ========================================================================
# OPERACIONES DEL TORNEO
# ========================================================================

def preparar_jugador(nombre, gamertag, email):
    """Valida y prepara los datos personales de un jugador antes de registrarlo o modificarlos."""
    nombre = validar_texto(nombre, "Nombre")
    gamertag = validar_texto(gamertag, "Gamertag", 30)
    email = email.strip()
    if not validar_email(email):
        raise ValueError("Formato de email inválido. Ejemplo: jugador@mail.com")
    return (nombre, gamertag, email)

def validar_gamertag_disponible(jugadores, gamertag, excluir_codigo=""):
    """Comprueba que un gamertag no esté siendo utilizado por otro jugador. Se ignoran mayúsculas."""
    ocupados = set()
    for i in range(len(jugadores)):
        if jugadores[i][0] != excluir_codigo:
            ocupados.add(jugadores[i][2].lower())
    if gamertag.lower() in ocupados:
        raise ValueError("Ese gamertag ya está registrado.")

def registrar_jugador(datos, codigo, nombre, gamertag, email):
    """Registra un nuevo jugador en la matriz, verificandolo previamente"""
    codigo = normalizar_codigo(codigo)

    if not validar_codigo_jugador(codigo):
        raise ValueError("El código debe tener 4 dígitos, desde JUG-0001 hasta JUG-9999.")

    if codigo in obtener_codigos(datos["jugadores"]):
        raise ValueError("Ese código de jugador ya existe.")

    nombre, gamertag, email = preparar_jugador(nombre, gamertag, email)
    validar_gamertag_disponible(datos["jugadores"], gamertag)

    datos["jugadores"].append([codigo, nombre, gamertag, email, ""])
    return codigo

def registrar_equipo(datos, codigo, nombre):
    """Registra un nuevo equipo en la matriz"""
    codigo = normalizar_codigo(codigo)

    if not validar_codigo_equipo(codigo):
        raise ValueError("El código debe tener 3 dígitos, desde EQ-001 hasta EQ-999.")

    if codigo in obtener_codigos(datos["equipos"]):
        raise ValueError("Ese código de equipo ya existe.")

    nombre = validar_texto(nombre, "Nombre del equipo")

    datos["equipos"].append([codigo, nombre])
    return codigo

def exigir_jugador(datos, codigo):
    """Busca un jugador por su código y devuelve la posición que ocupa en la matriz."""
    indice = buscar_jugador_por_codigo(
        datos["jugadores"], normalizar_codigo(codigo)
    )
    if indice == -1:
        raise ValueError("Jugador no encontrado.")
    return indice

def exigir_equipo(datos, codigo):
    """Busca un equipo mediante su código y devuelve su posición en la matriz."""
    indice = buscar_equipo_por_codigo(
        datos["equipos"], normalizar_codigo(codigo)
    )
    if indice == -1:
        raise ValueError("Equipo no encontrado.")
    return indice

def inscribir_jugador_en_equipo(datos, codigo_jugador, codigo_equipo):
    """Permite asociar un jugador a un equipo existente, verificando antes si ya existe o está registrado en otro equipo."""
    indice = exigir_jugador(datos, codigo_jugador)
    codigo_equipo = normalizar_codigo(codigo_equipo)
    exigir_equipo(datos, codigo_equipo)

    if datos["jugadores"][indice][4] != "":
        raise ValueError("El jugador ya tiene equipo. Desinscríbalo antes de cambiarlo.")

    datos["jugadores"][indice][4] = codigo_equipo
    
def desinscribir_jugador(datos, codigo):
    """Permite quitar la inscripción de un jugador a un equipo"""
    indice = exigir_jugador(datos, codigo)

    if datos["jugadores"][indice][4] == "":
        raise ValueError("El jugador ya está sin equipo.")

    datos["jugadores"][indice][4] = ""
    
def modificar_jugador(datos, codigo, nombre, gamertag, email):
    """Permite actualizar el nombre, gamertag y correo de un jugador registrado, conservando su código y equipo asignado."""
    indice = exigir_jugador(datos, codigo)
    nombre, gamertag, email = preparar_jugador(nombre, gamertag, email)
    validar_gamertag_disponible(datos["jugadores"], gamertag, datos["jugadores"][indice][0])

    # Se conservan el código y la inscripción del jugador.
    datos["jugadores"][indice][1:4] = [nombre, gamertag, email]
    
def modificar_equipo(datos, codigo, nombre):
    """Permite modificar el nombre de un equipo existente sin alterar su código identificador."""
    indice = exigir_equipo(datos, codigo)
    nombre = validar_texto(nombre, "Nombre del equipo")
    datos["equipos"][indice][1] = nombre
    
def validar_resultado(codigo1, codigo2, ganador, fase):
    """Comprueba que la fase de una partida sea válida, que el ganador corresponda
    a uno de los equipos participantes y que no se registren empates en las fases eliminatorias."""
    if fase not in FASES:
        raise ValueError("Fase inválida.")

    if ganador not in (codigo1, codigo2, "EMPATE"):
        raise ValueError("El ganador debe ser uno de los equipos de la partida.")

    if ganador == "EMPATE" and fase != "Grupos":
        raise ValueError("En semifinal o final debe registrar un ganador tras el desempate.")

def cargar_resultado(datos, codigo1, codigo2, ganador, fase):
    """Registra el resultado de una partida entre dos equipos existentes"""
    codigo1 = normalizar_codigo(codigo1)
    codigo2 = normalizar_codigo(codigo2)
    ganador = normalizar_codigo(ganador)

    exigir_equipo(datos, codigo1)
    exigir_equipo(datos, codigo2)

    if codigo1 == codigo2:
        raise ValueError("Un equipo no puede jugar contra sí mismo.")

    validar_resultado(codigo1, codigo2, ganador, fase)

    claves = set()

    for partida in datos["partidas"]:
        clave = clave_partida(partida[0], partida[1], partida[3])
        claves.add(clave)
    if clave_partida(codigo1, codigo2, fase) in claves:
        raise ValueError("Ese cruce ya está registrado en esa fase.")

    datos["partidas"].append([codigo1, codigo2, ganador, fase])

def exigir_numero_partida(datos, numero):
    """Verifica que el número de partida seleccionado sea válido y devuelve su posición correspondiente en la matriz."""
    # El usuario ve números desde 1; las listas usan índices desde 0.
    if type(numero) != int or numero < 1 or numero > len(datos["partidas"]):
        raise ValueError("Número de partida inexistente.")
    return numero - 1

def corregir_resultado(datos, numero, ganador):
    """Permite modificar el resultado de una partida existente, verificando que el nuevo ganador sea válido."""
    indice = exigir_numero_partida(datos, numero)
    partida = datos["partidas"][indice]
    ganador = normalizar_codigo(ganador)
    validar_resultado(partida[0], partida[1], ganador, partida[3])
    partida[2] = ganador


def eliminar_partida(datos, numero):
    """Elimina una partida registrada a partir del número seleccionado por el usuario."""
    indice = exigir_numero_partida(datos, numero)
    return datos["partidas"].pop(indice)

# ========================================================================
# CONSULTAS Y REPORTES
# ========================================================================

def calcular_victorias_equipo(partidas, codigo_eq):
    """Cuenta cuántas partidas ganó un equipo utilizando filter()."""
    victorias = list(filter(lambda p: p[2] == codigo_eq, partidas))
    return len(victorias)

def calcular_partidas_jugadas(partidas, codigo_eq):
    """Cuenta las partidas en las que participó un equipo, independientemente del resultado."""
    jugadas = list(filter(lambda p: p[0] == codigo_eq or p[1] == codigo_eq, partidas))
    return len(jugadas)

def actualizar_posiciones(datos):
    """Genera una tabla y ordena los equipos de mayor a menor cantidad de victorias."""
    posiciones = list(map(lambda equipo: [
        equipo[1], calcular_victorias_equipo(datos["partidas"], equipo[0]),
        calcular_partidas_jugadas(datos["partidas"], equipo[0])], datos["equipos"]))
    posiciones.sort(key=lambda fila: fila[1], reverse=True)
    return posiciones

def obtener_miembros(datos, codigo_eq):
    """Devuelve los jugadores que pertenecen a un equipo determinado."""
    return list(filter(lambda j: j[4] == codigo_eq, datos["jugadores"]))


def es_invicto(partidas, codigo):
    """Comprueba que un equipo haya jugado al menos una partida y que no haya perdido ninguna."""
    jugadas = list(filter(lambda p: p[0] == codigo or p[1] == codigo, partidas))
    perdidas = list(filter(lambda p: p[2] != codigo and p[2] != "EMPATE", jugadas))
    return len(jugadas) > 0 and len(perdidas) == 0

def reporte_equipos_invictos(datos):
    """utiliza la comprobación previa para devolver todos los equipos que cumplen la condición."""
    return list(filter(lambda eq: es_invicto(datos["partidas"], eq[0]), datos["equipos"]))

def buscar_jugador(jugadores, texto):
    """Busca coincidencias parciales en el nombre o gamertag del jugado"""
    busqueda = validar_texto(texto, "Búsqueda").lower()
    return list(filter(lambda j: busqueda in j[1].lower() or busqueda in j[2].lower(), jugadores))

def jugadores_disponibles(datos):
    """Diferencia de conjuntos: registrados menos quienes ya tienen equipo."""
    registrados = obtener_codigos(datos["jugadores"])
    inscriptos = set(map(lambda j: j[0], filter(lambda j: j[4] != "", datos["jugadores"])))
    disponibles = registrados - inscriptos
    return list(filter(lambda j: j[0] in disponibles, datos["jugadores"]))

def resumen_torneo(datos):
    total_victorias = reduce(lambda total, eq: total + calcular_victorias_equipo(
        datos["partidas"], eq[0]), datos["equipos"], 0)
    empates = len(list(filter(lambda p: p[2] == "EMPATE", datos["partidas"])))
    return {"jugadores": len(datos["jugadores"]), "equipos": len(datos["equipos"]),
            "partidas": len(datos["partidas"]), "victorias": total_victorias,
            "empates": empates, "sin_equipo": len(jugadores_disponibles(datos))}

def lineas_historial(datos):
    """Recorre todas las partidas registradas y genera una descripción para cada una."""
    lineas = []
    for i in range(len(datos["partidas"])):
        p = datos["partidas"][i]
        resultado = "Empate"
        if p[2] != "EMPATE":
            resultado = "Ganó: " + nombre_equipo(datos["equipos"], p[2])
        lineas.append(str(i + 1) + ". " + nombre_equipo(datos["equipos"], p[0]) +
                      " vs " + nombre_equipo(datos["equipos"], p[1]) +
                      " | " + resultado + " | Fase: " + p[3])
    return lineas

def generar_reporte(datos):
    """Genera un reporte de texto con la información actual del torneo."""
    resumen = resumen_torneo(datos)
    lineas = ["TOURNEYMANAGER - REPORTE DEL TORNEO", ""]
    for clave in resumen:
        lineas.append(clave.capitalize().replace("_", " ") + ": " + str(resumen[clave]))
    lineas.extend(["", "POSICIONES: EQUIPO | VICTORIAS | PARTIDAS"])
    posiciones = actualizar_posiciones(datos)
    for i in range(len(posiciones)):
        fila = posiciones[i]
        lineas.append(f"{fila[0]} | {fila[1]} | {fila[2]}")
    lineas.extend(["", "EQUIPOS E INTEGRANTES"])
    for i in range(len(datos["equipos"])):
        equipo = datos["equipos"][i]
        nombres = list(map(lambda j: j[1], obtener_miembros(datos, equipo[0])))
        if len(nombres) > 0:
            integrantes = ", ".join(nombres)
        else:
            integrantes = "Sin jugadores"
        lineas.append(equipo[1] + ": " + integrantes)
    lineas.extend(["", "HISTORIAL DE PARTIDAS"])
    lineas.extend(lineas_historial(datos))
    lineas.extend(["", "EQUIPOS INVICTOS"])
    lineas.extend(list(map(lambda eq: eq[1], reporte_equipos_invictos(datos))))
    return "\n".join(lineas) + "\n"

# ========================================================================
# LECTURA Y ESCRITURA DE ARCHIVOS
# ========================================================================

def validar_matriz(matriz, columnas, nombre):
    """Verifica que una matriz tenga la cantidad de columnas y los tipos de datos correctos."""
    if type(matriz) != list:
        raise ValueError(nombre + " debe ser una lista.")

    for i in range(len(matriz)):
        fila = matriz[i]
        if type(fila) != list or len(fila) != columnas:
            raise ValueError("Fila inválida en " + nombre + ".")
        for j in range(len(fila)):
            if type(fila[j]) != str:
                raise ValueError("Los campos de " + nombre + " deben ser textos.")

def validar_datos(datos):
    """Valida la estructura y el contenido de los datos del torneo."""
    if type(datos) != dict or set(datos.keys()) != {"jugadores", "equipos", "partidas"}:
        raise ValueError("La estructura debe contener jugadores, equipos y partidas.")

    validar_matriz(datos["equipos"], 2, "equipos")
    validar_matriz(datos["jugadores"], 5, "jugadores")
    validar_matriz(datos["partidas"], 4, "partidas")

    nuevos = crear_datos()

    for i in range(len(datos["equipos"])):
        eq = datos["equipos"][i]
        registrar_equipo(nuevos, eq[0], eq[1])
    for i in range(len(datos["jugadores"])):
        j = datos["jugadores"][i]
        registrar_jugador(nuevos, j[0], j[1], j[2], j[3])
        if j[4] != "":
            inscribir_jugador_en_equipo(nuevos, j[0], j[4])
    for i in range(len(datos["partidas"])):
        p = datos["partidas"][i]
        cargar_resultado(nuevos, p[0], p[1], p[2], p[3])
    return nuevos

def interpretar_json(texto):
    """Convierte un texto JSON en datos de Python y verifica que sean válidos."""
    contenido = json.loads(texto)
    return validar_datos(contenido)

def cargar_datos(ruta):
    """Lee un archivo JSON y recupera la información almacenada del torneo."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        texto = archivo.read()
    return interpretar_json(texto)

def guardar_datos(datos, ruta):
    """Valida y guarda la información del torneo en un archivo JSON."""
    validos = validar_datos(datos)
    texto = json.dumps(validos, ensure_ascii=False, indent=4)

    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(texto)

def guardar_reporte(texto, ruta):
    """Guarda el reporte del torneo en un archivo de texto TXT."""
    with open(ruta, "w", encoding="utf-8") as archivo:
        archivo.write(texto)

def leer_reporte(ruta):
    """Lee y devuelve el contenido de un archivo de texto TXT."""
    with open(ruta, "r", encoding="utf-8") as archivo:
        return archivo.read()
    
def borrar_reporte(ruta):
    """Elimina el archivo TXT e informa si no existe."""
    try:
        os.remove(ruta)
        print("Reporte TXT eliminado correctamente.")

    except FileNotFoundError:
        print("No hay ningún reporte TXT para eliminar.")
    
# ========================================================================
# PRESENTACIÓN EN CONSOLA
# ========================================================================

def mostrar_menu():
    """Muestra las categorías disponibles en el menú principal."""
    print("\n====== TOURNEYMANAGER ======")
    print("1. Gestión de jugadores")
    print("2. Gestión de equipos")
    print("3. Gestión de partidas")
    print("4. Consultas y estadísticas")
    print("5. Archivos y reportes")
    print("0. Guardar y salir")
    print()

def mostrar_submenu(categoria):
    """Muestra las opciones del submenú correspondiente a la categoría elegida."""
    opciones = {
        1: ("Registrar jugador", "Modificar jugador", "Buscar jugador",
            "Ver jugadores", "Ver jugadores sin equipo"),
        2: ("Registrar equipo", "Modificar nombre de equipo",
            "Inscribir jugador en equipo", "Desinscribir jugador",
            "Ver equipos y miembros"),
        3: ("Cargar resultado", "Corregir ganador o empate",
            "Eliminar partida errónea", "Ver historial de partidas"),
        4: ("Ver tabla de posiciones", "Ver equipos invictos"),
        5: ("Exportar reporte a TXT", "Leer último reporte guardado",
            "Guardar datos JSON", "Eliminar reporte TXT")
    }
    for i in range(len(opciones[categoria])):
        print(str(i + 1) + ". " + opciones[categoria][i])
    print("0. Volver al menú principal")
    return len(opciones[categoria])

def mostrar_jugadores(jugadores, equipos):
    """Muestra los datos de los jugadores registrados y sus equipos."""
    if len(jugadores) == 0:
        print("No hay jugadores para mostrar.")
    filas = list(map(lambda j: f"{j[0]} | {j[1]} | Tag: {j[2]} | " +
                     enmascarar_email(j[3]) + " | Equipo: " + nombre_equipo(equipos, j[4]), jugadores))
    for i in range(len(filas)):
        print(filas[i])

def mostrar_equipos_y_miembros(datos):
    """Muestra los equipos registrados junto con sus integrantes."""
    if len(datos["equipos"]) == 0:
        print("No hay equipos registrados.")
    for i in range(len(datos["equipos"])):
        eq = datos["equipos"][i]
        print("\n" + eq[0] + " - " + eq[1])
        nombres = list(map(lambda j: j[1], obtener_miembros(datos, eq[0])))
        if len(nombres) == 0:
            print("  Sin jugadores inscriptos.")
        for j in range(len(nombres)):
            print("  - " + nombres[j])

def mostrar_tabla_posiciones(datos):
    """Muestra las posiciones de los equipos y las estadísticas del torneo."""
    posiciones = actualizar_posiciones(datos)
    if len(posiciones) == 0:
        print("No hay equipos registrados.")
    print(f"{'EQUIPO':<60} {'VICTORIAS':>9} {'PARTIDAS':>9}")
    for i in range(len(posiciones)):
        fila = posiciones[i]
        print(f"{fila[0]:<60} {fila[1]:>9} {fila[2]:>9}")
    resumen = resumen_torneo(datos)
    print("Partidas registradas:", resumen["partidas"], "| Empates:", resumen["empates"])
    print("Total de victorias registradas:", resumen["victorias"])

def mostrar_invictos(datos):
    """Muestra los equipos que jugaron partidas sin registrar derrotas."""
    nombres = list(map(lambda eq: eq[1], reporte_equipos_invictos(datos)))
    if len(nombres) == 0:
        print("No hay equipos invictos que hayan jugado.")
    for i in range(len(nombres)):
        print(nombres[i])

def mostrar_historial_partidas(datos):
    """Muestra las partidas registradas y sus resultados."""
    lineas = lineas_historial(datos)
    if len(lineas) == 0:
        print("No hay partidas registradas.")
    for i in range(len(lineas)):
        print(lineas[i])
        
# ========================================================================
# ENTRADA DEL USUARIO
# ========================================================================

def pedir_texto(mensaje, maximo=60):
    """Solicita un texto, valida su contenido y permite cancelar la operación."""
    valido = False
    texto = ""
    while not valido:
        texto = input(mensaje).strip()
        if texto == "-1":
            raise ValueError("Operación cancelada.")
        try:
            texto = validar_texto(texto, "El dato", maximo)
            valido = True
        except ValueError as error:
            print(error)
    return texto

def pedir_codigo(mensaje, tipo):
    """Exige cuatro dígitos para jugadores o tres para equipos, sin completar ceros."""
    valido = False
    codigo = ""
    while not valido:
        numero = pedir_texto(mensaje)
        if tipo == "jugador":
            codigo = "JUG-" + numero
            valido = validar_codigo_jugador(codigo)
            if not valido:
                print("Ingrese exactamente 4 dígitos, desde 0001 hasta 9999.")
        elif tipo == "equipo":
            codigo = "EQ-" + numero
            valido = validar_codigo_equipo(codigo)
            if not valido:
                print("Ingrese exactamente 3 dígitos, desde 001 hasta 999.")
    return codigo

def pedir_opcion(mensaje, minimo, maximo, cancelar=True):
    """Solicita una opción numérica y verifica que esté dentro del rango permitido."""
    valido = False
    numero = minimo
    while not valido:
        texto = input(mensaje).strip()
        if cancelar and texto == "-1":
            raise ValueError("Operación cancelada.")
        try:
            numero = convertir_opcion(texto, minimo, maximo)
            valido = True
        except ValueError as error:
            print(error)
    return numero

def pedir_datos_jugador():
    """Solicita y valida los datos personales de un jugador."""
    nombre = pedir_texto("Nombre completo: ")
    gamertag = pedir_texto("Gamertag: ", 30)
    email = pedir_texto("Email: ", 254)

    while not validar_email(email):
        print("Email inválido. Ejemplo: jugador@mail.com")
        email = pedir_texto("Email: ", 254)

    return (nombre, gamertag, email)

def alta_jugador(datos):
    """Solicita los datos necesarios para registrar un nuevo jugador."""
    valido = False

    while not valido:
        codigo = pedir_codigo("Número del jugador (4 dígitos, 0001 a 9999): ", "jugador")

        if codigo in obtener_codigos(datos["jugadores"]):
            print("Ese código de jugador ya existe. Ingrese otro número.")
        else:
            valido = True

    nombre, gamertag, email = pedir_datos_jugador()
    registrar_jugador(datos, codigo, nombre, gamertag, email)
    
def alta_equipo(datos):
    """Solicita el código y nombre de un equipo para registrarlo en el torneo."""
    valido = False

    while not valido:
        codigo = pedir_codigo("Número del equipo (3 dígitos, 001 a 999): ", "equipo")

        if codigo in obtener_codigos(datos["equipos"]):
            print("Ese código de equipo ya existe. Ingrese otro número.")
        else:
            valido = True

    nombre = pedir_texto("Nombre del equipo: ")
    registrar_equipo(datos, codigo, nombre)
    
def inscripcion(datos):
    """Solicita los códigos de un jugador y un equipo para realizar su inscripción."""
    codigo_jug = pedir_codigo("Código del jugador: ", "jugador")
    exigir_jugador(datos, codigo_jug)
    codigo_eq = pedir_codigo("Código del equipo: ", "equipo")
    inscribir_jugador_en_equipo(datos, codigo_jug, codigo_eq)
    
def pedir_ganador(codigo1, codigo2, fase):
    """Solicita el resultado de una partida según los equipos y la fase."""
    print("1.", codigo1, "  2.", codigo2)
    maximo = 2

    if fase == "Grupos":
        print("3. Empate")
        maximo = 3

    opcion = pedir_opcion("Resultado: ", 1, maximo)
    opciones = (codigo1, codigo2, "EMPATE")

    return opciones[opcion - 1]

def alta_partida(datos):
    """Solicita los datos de una partida y registra su resultado en el torneo."""
    if len(datos["equipos"]) < 2:
        raise ValueError("Se necesitan al menos dos equipos registrados.")
    
    codigo1 = pedir_codigo("Código del equipo 1: ", "equipo")
    exigir_equipo(datos, codigo1)

    codigo2 = pedir_codigo("Código del equipo 2: ", "equipo")
    exigir_equipo(datos, codigo2)

    if codigo1 == codigo2:
        raise ValueError("Un equipo no puede jugar contra sí mismo.")
    for i in range(len(FASES)):
        print(str(i + 1) + ". " + FASES[i])
    
    opcion = pedir_opcion("Fase: ", 1, len(FASES))
    fase = FASES[opcion - 1]
    ganador = pedir_ganador(codigo1, codigo2, fase)
    cargar_resultado(datos, codigo1, codigo2, ganador, fase)
    
def editar_jugador(datos):
    """Solicita los nuevos datos de un jugador y actualiza su información."""
    codigo = pedir_codigo("Código del jugador a modificar: ", "jugador")
    indice = exigir_jugador(datos, codigo)

    mostrar_jugadores([datos["jugadores"][indice]], datos["equipos"])

    print("Ingrese los datos completos actualizados; el código y el equipo se conservan.")

    nombre, gamertag, email = pedir_datos_jugador()
    modificar_jugador(datos, codigo, nombre, gamertag, email)
    
def editar_equipo(datos):
    """Solicita un nuevo nombre y actualiza la información de un equipo."""
    codigo = pedir_codigo("Código del equipo: ", "equipo")
    exigir_equipo(datos, codigo)

    modificar_equipo(datos, codigo, pedir_texto("Nuevo nombre: "))

def seleccionar_partida(datos):
    """Muestra las partidas registradas y solicita seleccionar una por su número."""
    if len(datos["partidas"]) == 0:
        raise ValueError("No hay partidas registradas.")

    mostrar_historial_partidas(datos)
    return pedir_opcion("Número de partida: ", 1, len(datos["partidas"]))

def editar_partida(datos):
    """Permite corregir el ganador o empate de una partida registrada."""
    numero = seleccionar_partida(datos)
    p = datos["partidas"][numero - 1]

    ganador = pedir_ganador(p[0], p[1], p[3])
    corregir_resultado(datos, numero, ganador)

def borrar_partida(datos):
    """Solicita confirmación antes de eliminar una partida registrada."""
    numero = seleccionar_partida(datos)
    confirmacion = pedir_texto("Escriba ELIMINAR para confirmar o -1 para cancelar: ")

    if confirmacion != "ELIMINAR":
        raise ValueError("No se confirmó la eliminación.")

    eliminar_partida(datos, numero)

def ejecutar_modificacion(categoria, opcion, datos):
    """Ejecuta las operaciones que modifican los datos del torneo."""
    if categoria == 1:
        if opcion == 1:
            alta_jugador(datos)
        elif opcion == 2:
            editar_jugador(datos)

    elif categoria == 2:
        if opcion == 1:
            alta_equipo(datos)
        elif opcion == 2:
            editar_equipo(datos)
        elif opcion == 3:
            inscripcion(datos)
        elif opcion == 4:
            desinscribir_jugador(
                datos, pedir_codigo("Código del jugador: ", "jugador")
            )

    elif categoria == 3:
        if opcion == 1:
            alta_partida(datos)
        elif opcion == 2:
            editar_partida(datos)
        elif opcion == 3:
            borrar_partida(datos)

def ejecutar_consulta(categoria, opcion, datos, ruta_reporte):
    """Ejecuta las consultas y operaciones de archivos del torneo."""
    if categoria == 1:
        if opcion == 3:
            encontrados = buscar_jugador(
                datos["jugadores"],
                pedir_texto("Nombre o gamertag: ")
            )
            mostrar_jugadores(encontrados, datos["equipos"])
        elif opcion == 4:
            mostrar_jugadores(datos["jugadores"], datos["equipos"])
        elif opcion == 5:
            mostrar_jugadores(
                jugadores_disponibles(datos), datos["equipos"]
            )
    
    elif categoria == 2:
        if opcion == 5:
            mostrar_equipos_y_miembros(datos)
    
    elif categoria == 3:
        if opcion == 4:
            mostrar_historial_partidas(datos)
    
    elif categoria == 4:
        if opcion == 1:
            mostrar_tabla_posiciones(datos)
        elif opcion == 2:
            mostrar_invictos(datos)
    
    elif categoria == 5:
        if opcion == 1:
            guardar_reporte(generar_reporte(datos), ruta_reporte)
            print("Reporte guardado en", ruta_reporte)
        elif opcion == 2:
            print("REPORTE GUARDADO: puede diferir del estado actual si hubo cambios posteriores.")
            print(leer_reporte(ruta_reporte))
        elif opcion == 4:
            confirmacion = pedir_texto("Escriba ELIMINAR para borrar el reporte TXT: ")
            
            if confirmacion.upper() != "ELIMINAR":
                raise ValueError("No se confirmó la eliminación.")

            borrar_reporte(ruta_reporte)

# ========================================================================
# PROGRAMA PRINCIPAL
# ========================================================================

def iniciar_datos(ruta):
    """Recupera los datos guardados o inicia un torneo vacío si no existe el archivo."""
    try:
        datos = cargar_datos(ruta)
        print("Datos recuperados de", ruta)
        return datos
    except FileNotFoundError:
        print("No existe un guardado previo. Se inicia un torneo vacío.")
        return crear_datos()
    except (ValueError, UnicodeError) as error:
        print("El archivo de datos no es válido:", error)
        print("Revise el archivo JSON antes de continuar.")
    except OSError as error:
        print("No se pudo abrir el archivo:", error)
    return None

def intentar_guardar(datos, ruta):
    """Intenta guardar los datos del torneo e informa si la operación fue exitosa."""
    try:
        guardar_datos(datos, ruta)
        print("Datos guardados correctamente.")
        return True
    except (OSError, ValueError, UnicodeError) as error:
        print("No se pudieron guardar los datos:", error)
        print("Los cambios siguen en memoria. Puede intentar guardar nuevamente.")
        return False

def atender_opcion(categoria, opcion, datos, ruta_datos, ruta_reporte):
    """Ejecuta la opción seleccionada y devuelve si quedaron cambios sin guardar."""
    modificaciones = (
        (1, 1), (1, 2),
        (2, 1), (2, 2), (2, 3), (2, 4),
        (3, 1), (3, 2), (3, 3)
    )

    if (categoria, opcion) in modificaciones:
        ejecutar_modificacion(categoria, opcion, datos)
        print("Operación realizada.")
        return not intentar_guardar(datos, ruta_datos)
    if categoria == 5 and opcion == 3:
        return not intentar_guardar(datos, ruta_datos)
    ejecutar_consulta(categoria, opcion, datos, ruta_reporte)
    return None

def main():
    """Inicia el torneo y administra los menús, las operaciones y el guardado."""
    ruta_datos = "torneo.json"
    ruta_reporte = "reporte_torneo.txt"
    datos = iniciar_datos(ruta_datos)
    if datos is None:
        return
    continuar = True
    pendiente = False

    while continuar:
        mostrar_menu()
        if pendiente:
            print("ATENCIÓN: hay cambios pendientes de guardado.")
        try:
            categoria = pedir_opcion(
                "Seleccione una categoría: ", 0, 5, cancelar=False
            )
            if categoria == 0:
                guardado = intentar_guardar(datos, ruta_datos)
                pendiente = not guardado
                if guardado:
                    continuar = False
            else:
                volver = False
                while not volver:
                    cantidad_opciones = mostrar_submenu(categoria)
                    opcion = pedir_opcion(
                        "\nSeleccione una opción: ",
                        0,
                        cantidad_opciones,
                        cancelar=False
                    )
                    if opcion == 0:
                        volver = True
                    else:
                        try:
                            estado = atender_opcion(
                                categoria,
                                opcion,
                                datos,
                                ruta_datos,
                                ruta_reporte
                            )
                            if estado is not None:
                                pendiente = estado
                        except ValueError as error:
                            print(error)

                        except (OSError, UnicodeError) as error:
                            print("No se pudo acceder al archivo:", error)

        except ValueError as error:
            print(error)
        except (EOFError, KeyboardInterrupt):
            print("\nFin de entrada. Se intenta guardar antes de finalizar.")
            intentar_guardar(datos, ruta_datos)
            continuar = False
    print("Hasta luego.")


if __name__ == "__main__":
    main()