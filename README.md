# Synthetix Studio - Mini IDE (TDA)

**Universidad José Antonio Páez (UJAP)**  
**Asignatura:** Algoritmos y Estructuras de Datos II  
**Proyecto:** Primer Proyecto - Synthetix Studio  

## Descripción del Proyecto
Synthetix Studio es un entorno de desarrollo minimalista (Mini IDE) implementado en Python bajo el paradigma de **Programación Orientada a Objetos (POO)** y controlado mediante una **Consola de Línea de Comandos (CLI)** interactiva. 

Todas las estructuras de datos y algoritmos de ordenamiento fueron implementados totalmente desde cero sin hacer uso de estructuras o librerías nativas del lenguaje (`std::list`, `.sort()`, etc.).

---

## Estructura de Clases y Arquitectura

1. **Estructuras de Datos Propias:**
   * `Nodo`: Elemento básico enlazado.
   * `ListaEnlazada`: Gestiona dinámicamente los archivos o fragmentos de código abiertos en memoria.
   * `Pila (Stack)`: Utilizada para la verificación de balanceo de paréntesis/llaves (`check`) y para el sistema de control de cambios (`undo`/`redo`).
   * `Cola (Queue)`: Administra secuencialmente las solicitudes enviadas a la API de Inteligencia Artificial (`queue-status`, `analyze`).

2. **Motor de Ordenamiento (Algoritmos Manuales):**
   * `MotorOrdenamiento`: Implementa **MergeSort** ($O(N \log N)$) y **ShellSort** ($O(N^{1.5})$) para clasificar las alertas de código por número de línea o por nivel de gravedad (severidad).

3. **Módulo de Configuración e Integración HTTP:**
   * Carga de archivos `.json` mediante lectura externa de rutas y endpoints de la API.
   * Procesamiento secuencial de peticiones hacia la API mediante sockets/HTTP (`urllib`).

---

## Instrucciones de Compilación y Ejecución

1. Clonar el repositorio:
   ```bash
   git clone <URL_DE_TU_REPOSITTORIO>
   cd synthetix-studio