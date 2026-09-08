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


# BÚSQUEDA EN MATRICES

def buscar_jugador_por_codigo(codigo):
    # recorre la matriz y devuelve el indice del jugador, o -1 si no existe
    i = 0
    while i < len(jugadores):
        if jugadores[i][0] == codigo:
            return i
        i += 1
    return -1

def buscar_equipo_por_codigo(codigo):
    # recorre la matriz y devuelve el indice del equipo, o -1 si no existe
    i = 0
    while i < len(equipos):
        if equipos[i][0] == codigo:
            return i
        i += 1
    return -1

def codigo_jugador_existe(codigo):
    return buscar_jugador_por_codigo(codigo) != -1

def codigo_equipo_existe(codigo):
    return buscar_equipo_por_codigo(codigo) != -1


# FUNCIONES DE REGISTRO

def registrar_jugador():
    # agrega un nuevo jugador a la matriz de jugadores
    print("\n===== REGISTRAR JUGADOR =====")

    # pedir codigo y validar formato con regex
    while True:
        codigo = input("Código del jugador (formato JUG-XXXX, ej: JUG-0001): ").strip().upper()
        if not validar_codigo_jugador(codigo):
            print("  Código inválido. Debe ser JUG- seguido de 4 digitos.")
        elif codigo_jugador_existe(codigo):
            print("  Ese código ya esta registrado. Ingrese uno diferente.")
        else:
            break

    nombre = input("Nombre completo: ").strip()
    gamertag = input("Gamertag: ").strip()

    # pedir email y validar con regex
    while True:
        email = input("Email de contacto: ").strip()
        if validar_email(email):
            break
        print("  EMAIL INVÁLIDO. Ejemplo: jugador@mail.com")

    # agregar fila a la matriz de jugadores
    jugadores.append([codigo, nombre, gamertag, email, ""])
    print(f"\n  Jugador '{nombre}' registrado correctamente.")
    print(f"  Numero del codigo: {extraer_numero_codigo(codigo)}")
    print(f"  Email enmascarado: {enmascarar_email(email)}")


def registrar_equipo():
    # agrega un nuevo equipo a la matriz de equipos
    print("\n===== REGISTRAR EQUIPO =====")

    while True:
        codigo = input("Codigo del equipo (formato EQ-XXX, ej: EQ-001): ").strip().upper()
        if not validar_codigo_equipo(codigo):
            print("  CÓDIGO INVÁLIDO. Debe ser EQ- seguido de 3 digitos.")
        elif codigo_equipo_existe(codigo):
            print("  Ese código ya esta registrado. Ingrese uno diferente.")
        else:
            break

    nombre = input("Nombre del equipo: ").strip()

    # agregar fila a la matriz de equipos
    equipos.append([codigo, nombre])
    print(f"\n  Equipo '{nombre}' registrado correctamente.")


def inscribir_jugador_en_equipo():
    # modifica la columna codigo_equipo del jugador en la matriz
    print("\n===== INSCRIBIR JUGADOR EN EQUIPO =====")

    if len(jugadores) == 0:
        print("  No hay jugadores registrados.")
        return
    if len(equipos) == 0:
        print("  No hay equipos registrados.")
        return

    codigo_jug = input("Código del jugador (JUG-XXXX): ").strip().upper()
    idx_jug = buscar_jugador_por_codigo(codigo_jug)
    if idx_jug == -1:
        print("  Jugador no encontrado.")
        return

    codigo_eq = input("Código del equipo (EQ-XXX): ").strip().upper()
    idx_eq = buscar_equipo_por_codigo(codigo_eq)
    if idx_eq == -1:
        print("  Equipo no encontrado.")
        return

    # se modifica solo la columna 4 (codigo_equipo) del jugador
    jugadores[idx_jug][4] = codigo_eq
    print(f"\n  '{jugadores[idx_jug][1]}' inscripto en '{equipos[idx_eq][1]}'.")

