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
    """
    Valida el código ingresadao por el usario.
    Es decir que el código tenga formato JUG-XXXX (4 dígitos)
    """
    if re.match(r'^JUG-\d{4}$', codigo):
        return True
    else:
        return False

def validar_codigo_equipo(codigo):
    """
    Valida que el código ingresado por usuario.
    Asegura que el código tenga formato EQ-XXX (3 digitos)
    """
    if re.match(r'^EQ-\d{3}$', codigo):
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
    Oculta el usuario del email usando re.sub
    ej: usuario@mail.com -> XXXX@mail.com
    """
    resultado = re.sub(r'^[A-Za-z0-9._%+-]+', 'XXXX', email)

    return resultado


# BÚSQUEDA EN MATRICES

def buscar_jugador_por_codigo(codigo):
    """
    Recorre la matriz y devuelve el indice del jugador, o -1 si no existe
    """
    i = 0
    while i < len(jugadores):
        if jugadores[i][0] == codigo:
            return i
        i += 1
    return -1

def buscar_equipo_por_codigo(codigo):
    """
    Recorre la matriz y devuelve el indice del equipo, o -1 si no existe
    """
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
    """
    Agrega un nuevo jugador a la matriz de jugadores
    """
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
    """
    Agrega un nuevo equipo a la matriz de equipos
    """
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
    """
    Modifica la columna codigo_equipo del jugador en la matriz
    """
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


def cargar_resultado():
    """
    agrega el resultado de una partida a la matriz de partidas
    """
    print("\n===== CARGAR RESULTADO DE PARTIDA =====")

    if len(equipos) < 2:
        print("  Se necesitan al menos 2 equipos registrados.")
        return

    codigo_eq1 = input("Código del equipo 1 (EQ-XXX): ").strip().upper()
    if not codigo_equipo_existe(codigo_eq1):
        print("  EQUIPO 1 NO ENCONTRADO.")
        return

    codigo_eq2 = input("Código del equipo 2 (EQ-XXX): ").strip().upper()
    if not codigo_equipo_existe(codigo_eq2):
        print("  EQUIPO 2 NO ENCONTRADO.")
        return

    if codigo_eq1 == codigo_eq2:
        print("  El equipo no puede jugar contra si mismo.")
        return

    idx1 = buscar_equipo_por_codigo(codigo_eq1)
    idx2 = buscar_equipo_por_codigo(codigo_eq2)
    nombre1 = equipos[idx1][1]
    nombre2 = equipos[idx2][1]

    print(f"\n  {nombre1} vs {nombre2}")
    print("  ¿Quién ganó?")
    print("  1. " + nombre1)
    print("  2. " + nombre2)
    print("  3. Empate")
    opcion = input("  Opción: ").strip()

    if opcion == "1":
        ganador = codigo_eq1
    elif opcion == "2":
        ganador = codigo_eq2
    elif opcion == "3":
        ganador = "EMPATE"
    else:
        print("  OPCIÓN INVÁLIDA.")
        return

    print("\n  Fase del torneo:")
    print("  1. Grupos")
    print("  2. Semifinal")
    print("  3. Final")
    fase_op = input("  Opción: ").strip()
    fases = ["Grupos", "Semifinal", "Final"]

    if fase_op not in ["1", "2", "3"]:
        print("  OPCIÓN INVÁLIDA.")
        return

    fase = fases[int(fase_op) - 1]

    # agregar fila a la matriz de partidas
    partidas.append([codigo_eq1, codigo_eq2, ganador, fase])
    print("\n  Resultado cargado correctamente.")


# CONSULTA Y REPORTE

def mostrar_jugadores():
    """
    Muestra todos los jugadores usando map para formatear cada fila
    """
    print("\n===== LISTADO DE JUGADORES =====")
    if len(jugadores) == 0:
        print("  No hay jugadores registrados.")
        return

    # map: convierte cada fila de la matriz en un string legible
    filas = list(map(
        lambda j: f"  {j[0]} | {j[1]:<20} | Tag: {j[2]:<15} | {j[3]} | Equipo: {j[4] if j[4] else 'Sin equipo'}",
        jugadores
    ))

    i = 0
    while i < len(filas):
        print(filas[i])
        i += 1


def calcular_victorias_equipo(codigo_eq):
    """
    Utiliza filter para contar las partidas que ganó el equipo
    """
    victorias = list(filter(lambda p: p[2] == codigo_eq, partidas))
    return len(victorias)

def calcular_partidas_jugadas(codigo_eq):
    """
    Utiliza filter para contar las partidas en que participo el equipo
    """
    jugadas = list(filter(
        lambda p: p[0] == codigo_eq or p[1] == codigo_eq,
        partidas
    ))
    return len(jugadas)

def actualizar_posiciones():
    """
    Genera la información actual de cada equipo usando map
    """
    posiciones = list(map(
        lambda equipo: [
            equipo[1],
            calcular_victorias_equipo(equipo[0]),
            calcular_partidas_jugadas(equipo[0])
            ],
        equipos
        ))

    posiciones.sort(key=lambda fila: fila[1], reverse=True)

    return posiciones


def mostrar_tabla_posiciones():
    """
    Muestra la tabla de posiciones actualizada
    """
    print("\n===== TABLA DE POSICIONES =====")

    if len(equipos) == 0:
        print("  No hay equipos registrados.")
        return

    # obtiene las posiciones actuales
    posiciones = actualizar_posiciones()

    print(f"\n  {'EQUIPO':<25} {'VICTORIAS':>10} {'PARTIDAS':>10}")
    print("  " + "-" * 47)

    i = 0
    while i < len(posiciones):
        print(
            f"  {posiciones[i][0]:<25}"
            f" {posiciones[i][1]:>10}"
            f" {posiciones[i][2]:>10}" )
        i += 1

    # reduce: suma el total de victorias de todos los equipos
    total_victorias = reduce(
        lambda total, equipo: total + calcular_victorias_equipo(equipo[0]),
        equipos,
        0
        )

    print(f"\n  Total de victorias disputadas: {total_victorias}")

def mostrar_equipos_y_miembros():
    """
    Muestra cada equipo con sus jugadores usando filter y map
    """
    print("\n===== EQUIPOS Y JUGADORES =====")
    if len(equipos) == 0:
        print("  No hay equipos registrados.")
        return

    i = 0
    while i < len(equipos):
        codigo_eq = equipos[i][0]
        nombre_eq = equipos[i][1]

        # filter: obtiene los jugadores de este equipo
        miembros = list(filter(lambda j: j[4] == codigo_eq, jugadores))

        # map: extrae solo los nombres
        nombres = list(map(lambda j: j[1], miembros))

        print(f"\n  {nombre_eq} ({codigo_eq})")
        if len(nombres) == 0:
            print("    Sin jugadores inscriptos.")
        else:
            j = 0
            while j < len(nombres):
                print(f"    - {nombres[j]}")
                j += 1
        i += 1


def reporte_equipos_invictos():
    """
    Reporta los equipos que jugaron y no perdieron ninguna partida
    """
    print("\n===== EQUIPOS INVICTOS =====")
    if len(equipos) == 0:
        print("  No hay equipos registrados.")
        return

    def es_invicto(eq):
        codigo = eq[0]
        # filter: partidas en las que participó el equipo
        jugadas = list(filter(
            lambda p: p[0] == codigo or p[1] == codigo,
            partidas
        ))
        if len(jugadas) == 0:
            return False
        # filter: partidas en las que perdió el equipo
        perdidas = list(filter(
            lambda p: (p[0] == codigo or p[1] == codigo)
                      and p[2] != codigo
                      and p[2] != "EMPATE",
            jugadas
        ))
        return len(perdidas) == 0

    # filter: equipos que cumplan la condición de invicto
    invictos = list(filter(es_invicto, equipos))

    if len(invictos) == 0:
        print("  No hay equipos invictos actualmente.")
    else:
        # map: extrae los nombres de los equipos invictos
        nombres = list(map(lambda eq: eq[1], invictos))
        i = 0
        while i < len(nombres):
            print(f"  - {nombres[i]}")
            i += 1


def buscar_jugador():
    """
    Busca jugadores por nombre o gamertag usando filter
    """
    print("\n===== BUSCAR JUGADOR =====")
    if len(jugadores) == 0:
        print("  No hay jugadores registrados.")
        return

    busqueda = input("Ingrese nombre o gamertag a buscar: ").strip().lower()

    # filter: jugadores que su nombre o gamertag contengan lo buscado
    resultados = list(filter(
        lambda j: busqueda in j[1].lower() or busqueda in j[2].lower(),
        jugadores
    ))

    if len(resultados) == 0:
        print("  No se encontraron jugadores.")
    else:
        print(f"\n  Se encontraron {len(resultados)} resultado(s):")
        i = 0
        while i < len(resultados):
            j = resultados[i]
            equipo_str = j[4] if j[4] else "Sin equipo"
            print(f"  {j[0]} | {j[1]} | Gamertag: {j[2]} | Equipo: {equipo_str}")
            i += 1


def mostrar_historial_partidas():
    """
    Muestra todas las partidas cargadas en la matriz
    """
    print("\n===== HISTORIAL DE PARTIDAS =====")
    if len(partidas) == 0:
        print("  No hay partidas registradas.")
        return

    i = 0
    while i < len(partidas):
        p = partidas[i]
        idx1 = buscar_equipo_por_codigo(p[0])
        idx2 = buscar_equipo_por_codigo(p[1])
        nombre1 = equipos[idx1][1] if idx1 != -1 else p[0]
        nombre2 = equipos[idx2][1] if idx2 != -1 else p[1]

        if p[2] == "EMPATE":
            resultado_str = "Empate"
        else:
            idx_gan = buscar_equipo_por_codigo(p[2])
            resultado_str = "Ganó: " + (equipos[idx_gan][1] if idx_gan != -1 else p[2])

        print(f"  {nombre1} vs {nombre2} | {resultado_str} | Fase: {p[3]}")
        i += 1


# MENÚ PRINCIPAL

def mostrar_menu():
    print("\n" + "=" * 50)
    print("       TOURNEYMANAGER - Gestión de Torneos")
    print("=" * 50)
    print("   1.  Registrar jugador")
    print("   2.  Registrar equipo")
    print("   3.  Inscribir jugador en equipo")
    print("   4.  Cargar resultado de partida")
    print("   5.  Ver jugadores")
    print("   6.  Ver equipos y miembros")
    print("   7.  Ver tabla de posiciones")
    print("   8.  Ver equipos invictos")
    print("   9.  Buscar jugador")
    print("  10.  Ver historial de partidas")
    print("   0.  Salir")
    print("=" * 50)


def main():
    print("\n  BIENVENIDO A TOURNEYMANAGER")
    print("  Sistema de Gestion de Torneos de Videojuegos")

    continuar = True
    while continuar:
        mostrar_menu()
        opcion = input("Seleccione una opción: ").strip()

        if opcion == "1":
            registrar_jugador()
        elif opcion == "2":
            registrar_equipo()
        elif opcion == "3":
            inscribir_jugador_en_equipo()
        elif opcion == "4":
            cargar_resultado()
        elif opcion == "5":
            mostrar_jugadores()
        elif opcion == "6":
            mostrar_equipos_y_miembros()
        elif opcion == "7":
            mostrar_tabla_posiciones()
        elif opcion == "8":
            reporte_equipos_invictos()
        elif opcion == "9":
            buscar_jugador()
        elif opcion == "10":
            mostrar_historial_partidas()
        elif opcion == "0":
            print("\n  ¡Hasta luego!")
            continuar = False
        else:
            print("  OPCIÓN INVÁLIDA. Intente nuevamente.")


main()
