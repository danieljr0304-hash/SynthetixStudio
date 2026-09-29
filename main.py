import json
import os
import sys
import urllib.request
import urllib.error

# ==========================================
# 1. ESTRUCTURAS DE DATOS PROPIAS (DESDE CERO)
# ==========================================

class Nodo:
    """Nodo genérico para estructuras enlazadas."""
    def __init__(self, dato):
        self.dato = dato
        self.siguiente = None


class ListaEnlazada:
    """Lista enlazada simple para gestionar los archivos abiertos."""
    def __init__(self):
        self.cabeza = None
        self._tamano = 0

    def agregar(self, dato):
        nuevo = Nodo(dato)
        if not self.cabeza:
            self.cabeza = nuevo
        else:
            actual = self.cabeza
            while actual.siguiente:
                actual = actual.siguiente
            actual.siguiente = nuevo
        self._tamano += 1

    def eliminar_por_nombre_o_index(self, identificador):
        actual = self.cabeza
        anterior = None
        idx = 0

        while actual:
            es_match = False
            if str(identificador).isdigit() and int(identificador) == idx:
                es_match = True
            elif hasattr(actual.dato, 'nombre') and actual.dato.nombre == identificador:
                es_match = True

            if es_match:
                if anterior is None:
                    self.cabeza = actual.siguiente
                else:
                    anterior.siguiente = actual.siguiente
                self._tamano -= 1
                return actual.dato

            anterior = actual
            actual = actual.siguiente
            idx += 1

        return None

    def buscar(self, identificador):
        actual = self.cabeza
        idx = 0
        while actual:
            if str(identificador).isdigit() and int(identificador) == idx:
                return actual.dato
            elif hasattr(actual.dato, 'nombre') and actual.dato.nombre == identificador:
                return actual.dato
            actual = actual.siguiente
            idx += 1
        return None

    def esta_vacia(self):
        return self.cabeza is None

    def tamano(self):
        return self._tamano


class Pila:
    """Pila LIFO implementada con nodos enlazados desde cero."""
    def __init__(self):
        self.tope = None
        self._tamano = 0

    def push(self, dato):
        nuevo = Nodo(dato)
        nuevo.siguiente = self.tope
        self.tope = nuevo
        self._tamano += 1

    def pop(self):
        if self.esta_vacia():
            return None
        dato = self.tope.dato
        self.tope = self.tope.siguiente
        self._tamano -= 1
        return dato

    def peek(self):
        if self.esta_vacia():
            return None
        return self.tope.dato

    def esta_vacia(self):
        return self.tope is None

    def tamano(self):
        return self._tamano


class Cola:
    """Cola FIFO implementada con nodos enlazados desde cero."""
    def __init__(self):
        self.frente = None
        self.final = None
        self._tamano = 0

    def enqueue(self, dato):
        nuevo = Nodo(dato)
        if self.esta_vacia():
            self.frente = nuevo
            self.final = nuevo
        else:
            self.final.siguiente = nuevo
            self.final = nuevo
        self._tamano += 1

    def dequeue(self):
        if self.esta_vacia():
            return None
        dato = self.frente.dato
        self.frente = self.frente.siguiente
        if self.frente is None:
            self.final = None
        self._tamano -= 1
        return dato

    def esta_vacia(self):
        return self.frente is None

    def tamano(self):
        return self._tamano


# ==========================================
# 2. MODELOS Y ALGORITMOS DE ORDENAMIENTO
# ==========================================

class Diagnostico:
    """Representa una alerta o advertencia de análisis estático de código."""
    def __init__(self, linea, severidad, mensaje):
        self.linea = linea          # int
        self.severidad = severidad  # int (1: Baja, 2: Media, 3: Alta, 4: Crítica)
        self.mensaje = mensaje

    def __str__(self):
        sev_map = {1: "Baja", 2: "Media", 3: "Alta", 4: "Critica"}
        return f"[Línea {self.linea}] (Gravedad: {sev_map.get(self.severidad, self.severidad)}) -> {self.mensaje}"


class MotorOrdenamiento:
    """Implementación manual de MergeSort y ShellSort."""
    
    @staticmethod
    def _obtener_clave(diag, criterio):
        if criterio == "line":
            return diag.linea
        elif criterio == "severity":
            return diag.severidad
        return diag.linea

    @classmethod
    def mergesort(cls, lista_diag, criterio="line"):
        if len(lista_diag) <= 1:
            return lista_diag

        medio = len(lista_diag) // 2
        izquierda = cls.mergesort(lista_diag[:medio], criterio)
        derecha = cls.mergesort(lista_diag[medio:], criterio)

        return cls._mezclar(izquierda, derecha, criterio)

    @classmethod
    def _mezclar(cls, izq, der, criterio):
        resultado = []
        i = j = 0
        while i < len(izq) and j < len(der):
            clave_i = cls._obtener_clave(izq[i], criterio)
            clave_j = cls._obtener_clave(der[j], criterio)

            if clave_i <= clave_j:
                resultado.append(izq[i])
                i += 1
            else:
                resultado.append(der[j])
                j += 1

        while i < len(izq):
            resultado.append(izq[i])
            i += 1
        while j < len(der):
            resultado.append(der[j])
            j += 1

        return resultado

    @classmethod
    def shellsort(cls, lista_diag, criterio="line"):
        arr = list(lista_diag)
        n = len(arr)
        gap = n // 2

        while gap > 0:
            for i in range(gap, n):
                temp = arr[i]
                j = i
                clave_temp = cls._obtener_clave(temp, criterio)

                while j >= gap and cls._obtener_clave(arr[j - gap], criterio) > clave_temp:
                    arr[j] = arr[j - gap]
                    j -= gap

                arr[j] = temp
            gap //= 2

        return arr


# ==========================================
# 3. DOMINIO DEL MINI IDE (SYNTHETIX STUDIO)
# ==========================================

class ArchivoCodigo:
    """Representa un archivo abierto en la sesión con historial Undo/Redo."""
    def __init__(self, nombre, contenido_inicial=""):
        self.nombre = nombre
        self.contenido = contenido_inicial
        self.pila_undo = Pila()
        self.pila_redo = Pila()
        self.diagnosticos = []

    def actualizar_contenido(self, nuevo_contenido):
        # Guardar el estado anterior antes de modificar
        self.pila_undo.push(self.contenido)
        # Al hacer un cambio nuevo, la pila de rehacer se limpia
        self.pila_redo = Pila()
        self.contenido = nuevo_contenido

    def undo(self):
        if self.pila_undo.esta_vacia():
            return False
        self.pila_redo.push(self.contenido)
        self.contenido = self.pila_undo.pop()
        return True

    def redo(self):
        if self.pila_redo.esta_vacia():
            return False
        self.pila_undo.push(self.contenido)
        self.contenido = self.pila_redo.pop()
        return True


class VerificadorSintaxis:
    """Valida anidamiento de símbolos mediante Pila."""
    @staticmethod
    def verificar(codigo):
        pila = Pila()
        parejas = {')': '(', '}': '{', ']': '['}
        apertura = set(['(', '{', '['])
        cierre = set([')', '}', ']'])

        lineas = codigo.split('\n')
        for nro_linea, linea in enumerate(lineas, 1):
            for col, char in enumerate(linea, 1):
                if char in apertura:
                    pila.push((char, nro_linea, col))
                elif char in cierre:
                    if pila.esta_vacia():
                        return False, f"Error en línea {nro_linea}, col {col}: '<b>{char}</b>' de cierre sin apertura."
                    top_char, top_linea, top_col = pila.pop()
                    if parejas[char] != top_char:
                        return False, f"Error en línea {nro_linea}, col {col}: Se esperaba cierre para '<b>{top_char}</b>' (de línea {top_linea}), pero se encontró '<b>{char}</b>'."

        if not pila.esta_vacia():
            top_char, top_linea, top_col = pila.pop()
            return False, f"Error: El símbolo '<b>{top_char}</b>' en la línea {top_linea}, col {top_col} no fue cerrado."

        return True, "Sintaxis de delimitadores correcta y balanceada."


# ==========================================
# 4. CONSOLA DE LÍNEA DE COMANDOS (CLI)
# ==========================================

class SynthetixStudioCLI:
    """Controlador principal de la Consola CLI del Mini IDE."""
    def __init__(self):
        self.archivos = ListaEnlazada()
        self.archivo_activo = None
        self.cola_peticiones = Cola()
        self.configuracion = {}
        self.cargar_datos_defecto()

    def cargar_datos_defecto(self):
        """Precarga archivos iniciales para pruebas directas."""
        f1 = ArchivoCodigo("main.cpp", "int main() {\n    if (x > 0) {\n        return 0;\n    }\n}")
        f2 = ArchivoCodigo("utils.py", "def calcular(a, b):\n    resultado = (a + b\n    return resultado")
        
        # Generar diagnósticos de prueba para f1
        f1.diagnosticos = [
            Diagnostico(12, 3, "Variable no utilizada 'temp'"),
            Diagnostico(4, 1, "Falta espacio después de coma"),
            Diagnostico(25, 4, "Posible desbordamiento de buffer"),
            Diagnostico(8, 2, "Función demasiado larga (más de 50 líneas)")
        ]

        self.archivos.agregar(f1)
        self.archivos.agregar(f2)
        self.archivo_activo = f1

    def ejecutar_comando(self, linea_comando):
        partes = linea_comando.strip().split(maxsplit=2)
        if not partes:
            return

        cmd = partes[0].lower()

        # 1. ARCHIVOS Y CONFIGURACIÓN
        if cmd == "new":
            if len(partes) < 2:
                print("Uso: new <nombre_archivo> [contenido]")
                return
            nombre = partes[1]
            contenido = partes[2] if len(partes) > 2 else "// Contenido inicial"
            nuevo = ArchivoCodigo(nombre, contenido)
            self.archivos.agregar(nuevo)
            self.archivo_activo = nuevo
            print(f"[+] Archivo '{nombre}' creado y establecido como activo.")

        elif cmd == "list":
            if self.archivos.esta_vacia():
                print("[-] No hay archivos abiertos en la sesión.")
                return
            print("\n--- ARCHIVOS ABIERTOS ---")
            actual = self.archivos.cabeza
            idx = 0
            while actual:
                f = actual.dato
                activo_str = " (ACTIVO)" if f == self.archivo_activo else ""
                print(f"[{idx}] {f.nombre}{activo_str}")
                actual = actual.siguiente
                idx += 1
            print()

        elif cmd == "switch":
            if len(partes) < 2:
                print("Uso: switch <id_o_nombre>")
                return
            target = partes[1]
            encontrado = self.archivos.buscar(target)
            if encontrado:
                self.archivo_activo = encontrado
                print(f"[*] Cambiado a archivo activo: '{encontrado.nombre}'")
            else:
                print(f"[-] No se encontró el archivo '{target}'.")

        elif cmd == "delete":
            if len(partes) < 2:
                print("Uso: delete <id_o_nombre>")
                return
            target = partes[1]
            eliminado = self.archivos.eliminar_por_nombre_o_index(target)
            if eliminado:
                print(f"[-] Archivo '{eliminado.nombre}' eliminado de memoria.")
                if self.archivo_activo == eliminado:
                    self.archivo_activo = self.archivos.cabeza.dato if self.archivos.cabeza else None
            else:
                print(f"[-] No se pudo eliminar. Archivo '{target}' no encontrado.")

        elif cmd == "config":
            ruta = partes[1] if len(partes) > 1 else "config.json"
            if os.path.exists(ruta):
                try:
                    with open(ruta, "r") as file:
                        self.configuracion = json.load(file)
                    print(f"[+] Configuración cargada con éxito desde '{ruta}':")
                    print(f"    - Endpoint API: {self.configuracion.get('api_endpoint')}")
                    print(f"    - Logs Dir: {self.configuracion.get('logs_dir')}")
                except Exception as e:
                    print(f"[-] Error al leer la configuración: {e}")
            else:
                print(f"[-] El archivo '{ruta}' no existe.")

        # 2. VALIDACIÓN E HISTORIAL
        elif cmd == "check":
            if not self.archivo_activo:
                print("[-] No hay ningún archivo activo.")
                return
            ok, msj = VerificadorSintaxis.verificar(self.archivo_activo.contenido)
            if ok:
                print(f"[SINTAXIS OK] {msj}")
            else:
                print(f"[SINTAXIS ERROR] {msj}")

        elif cmd == "undo":
            if not self.archivo_activo:
                print("[-] No hay archivo activo.")
                return
            if self.archivo_activo.undo():
                print(f"[+] Undo realizado en '{self.archivo_activo.nombre}'.")
            else:
                print("[-] No hay cambios para deshacer.")

        elif cmd == "redo":
            if not self.archivo_activo:
                print("[-] No hay archivo activo.")
                return
            if self.archivo_activo.redo():
                print(f"[+] Redo realizado en '{self.archivo_activo.nombre}'.")
            else:
                print("[-] No hay cambios para rehacer.")

        # EDITAR CÓDIGO (Auxiliar para probar Undo/Redo)
        elif cmd == "edit":
            if not self.archivo_activo:
                print("[-] No hay archivo activo.")
                return
            if len(partes) < 2:
                print("Uso: edit <nuevo_codigo>")
                return
            nuevo_txt = partes[1] if len(partes) == 2 else partes[1] + " " + partes[2]
            self.archivo_activo.actualizar_contenido(nuevo_txt)
            print(f"[+] Código de '{self.archivo_activo.nombre}' actualizado.")

        # 3. MOTOR DE ORDENAMIENTO
        elif cmd == "sort":
            if not self.archivo_activo or not self.archivo_activo.diagnosticos:
                print("[-] El archivo activo no posee diagnósticos para ordenar.")
                return
            
            criterio = "line"
            algoritmo = "mergesort"

            if len(partes) >= 2:
                criterio = partes[1].lower()
            if len(partes) >= 3:
                algoritmo = partes[2].lower()

            if criterio not in ["line", "severity"]:
                print("[-] Criterio no válido. Use 'line' o 'severity'.")
                return

            print(f"\n--- Diagnósticos Ordenados por [{criterio}] usando [{algoritmo}] ---")
            if algoritmo == "shellsort":
                res = MotorOrdenamiento.shellsort(self.archivo_activo.diagnosticos, criterio)
            else:
                res = MotorOrdenamiento.mergesort(self.archivo_activo.diagnosticos, criterio)

            for d in res:
                print(f"  {d}")
            print()

        # 4. BUFFER DE PETICIONES
        elif cmd == "queue-status":
            print(f"\n--- ESTADO DE LA COLA DE PETICIONES IA ---")
            print(f"Peticiones pendientes en cola: {self.cola_peticiones.tamano()}")
            actual = self.cola_peticiones.frente
            i = 1
            while actual:
                print(f"  {i}. Solicitud para el archivo '{actual.dato.nombre}'")
                actual = actual.siguiente
                i += 1
            print()

        # 5. INTEGRACIÓN CON IA (COLAS + HTTP)
        elif cmd == "analyze":
            if not self.archivo_activo:
                print("[-] No hay archivo activo para analizar.")
                return

            # Encolar petición
            self.cola_peticiones.enqueue(self.archivo_activo)
            print(f"[+] Solicitud para '{self.archivo_activo.nombre}' añadida a la cola FIFO.")

            # Procesar la cola secuencialmente
            self.procesar_cola_ia()

        elif cmd == "show":
            if not self.archivo_activo:
                print("[-] No hay archivo activo.")
                return
            print(f"\n--- {self.archivo_activo.nombre} ---")
            print(self.archivo_activo.contenido)
            print("--------------------\n")

        elif cmd == "help":
            self.mostrar_ayuda()

        elif cmd == "exit":
            print("Cerrando Synthetix Studio...")
            sys.exit(0)

        else:
            print(f"[-] Comando no reconocido: '{cmd}'. Escriba 'help' para ver los comandos.")

    def procesar_cola_ia(self):
        """Despacha las peticiones secuencialmente invocando la API de IA."""
        endpoint = self.configuracion.get("api_endpoint", "https://api.synthetix.ai/v1/analyze")
        
        while not self.cola_peticiones.esta_vacia():
            archivo = self.cola_peticiones.dequeue()
            print(f"\n[*] Procesando solicitud HTTP para '{archivo.nombre}' desde la cola...")
            
            # Intento de petición HTTP real con fallback simulado
            payload = json.dumps({"code": archivo.contenido, "file": archivo.nombre}).encode('utf-8')
            req = urllib.request.Request(endpoint, data=payload, headers={'Content-Type': 'application/json'})
            
            try:
                with urllib.request.urlopen(req, timeout=3) as response:
                    res_body = response.read().decode('utf-8')
                    print(f"[RESPUESTA API IA HTTP 200]: {res_body}")
            except Exception:
                # Simulación de respuesta IA requerida en la práctica
                print(f"[RESPUESTA IA - SIMULADA]")
                print(f"  - Archivo: {archivo.nombre}")
                print(f"  - Complejidad Temporal (Big O): O(N log N)")
                print(f"  - Propuesta de Refactorización: Optimizar bucle redundante en las líneas centrales.")

    def mostrar_ayuda(self):
        print("""
======================================================
               SYNTHETIX STUDIO - CLI
======================================================
Comandos Disponibles:
  new <nombre> [contenido]  : Crear un nuevo archivo en memoria.
  list                      : Listar todos los archivos abiertos.
  switch <id/nombre>        : Cambiar el archivo activo actual.
  delete <id/nombre>        : Eliminar archivo liberando memoria.
  config <ruta>             : Cargar archivo de configuración .json.
  show                      : Ver el contenido del archivo activo.
  edit <nuevo_texto>        : Editar el código del archivo activo.
  check                     : Validar balanceo de delimitadores (Stack).
  undo                      : Deshacer el último cambio de código.
  redo                      : Rehacer el cambio deshecho.
  sort <line|severity> <mergesort|shellsort> : Ordenar advertencias.
  queue-status              : Ver estado de la cola FIFO para la API IA.
  analyze                   : Encolar y enviar código a la API de IA.
  help                      : Mostrar este panel de comandos.
  exit                      : Salir del programa.
======================================================
""")

    def iniciar(self):
        print("======================================================")
        print("      SYNTHETIX STUDIO - Mini IDE (TDA 2026)")
        print("======================================================")
        print("Escriba 'help' para ver la lista de comandos CLI.\n")
        
        # Cargar config por defecto si existe
        if os.path.exists("config.json"):
            self.ejecutar_comando("config config.json")

        while True:
            try:
                prompt = f"SynthetixStudio ({self.archivo_activo.nombre if self.archivo_activo else 'Sin Archivo'})> "
                linea = input(prompt)
                self.ejecutar_comando(linea)
            except (KeyboardInterrupt, EOFError):
                print("\nSaliendo...")
                break


if __name__ == "__main__":
    app = SynthetixStudioCLI()
    app.iniciar()