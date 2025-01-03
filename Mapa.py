from OpenGL.GL import *
from OpenGL.GLU import *
from Configuracion_Mapa import Calles
import math
import heapq

class Mapa:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grafo = {}  # Diccionario para almacenar el grafo.
        self.crear_grafo()

    def crear_grafo(self):
        """Crea un grafo a partir de las calles."""
        self.nodos = {}
        node_id = 0

        for calle in Calles.values():
            origen = calle["origen"]
            destino = calle["destino"]

            # Asignar IDs únicos a los nodos.
            if origen not in self.nodos:
                self.nodos[origen] = node_id
                node_id += 1
            if destino not in self.nodos:
                self.nodos[destino] = node_id
                node_id += 1

            origen_id = self.nodos[origen]
            destino_id = self.nodos[destino]

            # Calcular la distancia (peso) entre los nodos.
            distancia = math.hypot(destino[0] - origen[0], destino[1] - origen[1])

            # Agregar aristas al grafo (no dirigido).
            self.grafo.setdefault(origen_id, []).append((destino_id, distancia))
            self.grafo.setdefault(destino_id, []).append((origen_id, distancia))

    def inicializar_opengl(self):
        """Inicializa las configuraciones de OpenGL."""
        glClearColor(0.75, 1.0, 0.5, 1.0)  # Fondo verde claro.
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)  # Coordenadas 2D.
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def dibujar_calles(self):
        """Dibuja las calles en el mapa."""
        glColor3f(0, 0, 0)  # Color negro para las líneas.
        glLineWidth(2.0)  # Grosor de las líneas.
        glBegin(GL_LINES)
        for calle in Calles.values():
            x1, y1 = calle["origen"]
            x2, y2 = calle["destino"]
            glVertex2f(x1, y1)
            glVertex2f(x2, y2)
        glEnd()

    def dibujar_intersecciones(self):
        """Dibuja las intersecciones como puntos en el mapa."""
        glColor3f(1, 0, 0)  # Color rojo para las intersecciones.
        glPointSize(5)  # Tamaño de los puntos.
        glBegin(GL_POINTS)
        intersecciones = {calle["origen"] for calle in Calles.values()} | {calle["destino"] for calle in Calles.values()}
        for x, y in intersecciones:
            glVertex2f(x, y)
        glEnd()

    def display(self):
        """Función de display para GLUT."""
        glClear(GL_COLOR_BUFFER_BIT)  # Limpia la pantalla.
        self.dibujar_calles()  # Dibuja las calles.
        self.dibujar_intersecciones()  # Dibuja las intersecciones.
        glFlush()  # Asegura que se renderice el contenido.

    def encontrar_camino_mas_corto(self, origen_coord, destino_coord):
        """
        Encuentra el camino más corto entre dos coordenadas.
        - `origen_coord`: Coordenadas del punto de origen (x, y).
        - `destino_coord`: Coordenadas del punto de destino (x, y).
        """
        # Convierte las coordenadas a tuplas, ya que las listas no son hashables.
        origen_coord = tuple(origen_coord)
        destino_coord = tuple(destino_coord)

        origen_id = self.nodos.get(origen_coord)
        destino_id = self.nodos.get(destino_coord)

        if origen_id is None or destino_id is None:
            print("Origen o destino no existen en el mapa.")
            return []

        # Implementación del algoritmo de Dijkstra.
        cola = [(0, origen_id, [])]
        visitados = set()

        while cola:
            (costo, nodo_actual, camino) = heapq.heappop(cola)
            if nodo_actual in visitados:
                continue

            visitados.add(nodo_actual)
            camino = camino + [nodo_actual]

            if nodo_actual == destino_id:
                # Convertir IDs de nodos a coordenadas.
                camino_coords = [list(self.nodos.keys())[list(self.nodos.values()).index(n)] for n in camino]
                return camino_coords

            for vecino, peso in self.grafo.get(nodo_actual, []):
                if vecino not in visitados:
                    heapq.heappush(cola, (costo + peso, vecino, camino))

        print("No se encontró un camino.")
        return []

    def resaltar_calle(self, origen, destino):
        """Resalta una calle entre dos nodos."""
        for calle in Calles.values():
            if (calle['origen'] == origen and calle['destino'] == destino) or \
                    (calle['destino'] == origen and calle['origen'] == destino):
                glColor3f(1, 0, 0)  # Color rojo para resaltar.
                glLineWidth(4.0)  # Línea más gruesa.
                glBegin(GL_LINES)
                glVertex2f(*calle['origen'])
                glVertex2f(*calle['destino'])
                glEnd()
                glFlush()
                return
        print("Calle no encontrada para resaltar.")

    def resaltar_calle(self, origen, destino, color=(1, 0, 0)):
        """
        Dibuja una línea entre dos nodos para resaltar una calle.
        - `origen`: Coordenadas del nodo origen.
        - `destino`: Coordenadas del nodo destino.
        - `color`: Color de la línea (por defecto, rojo).
        """
        glColor3f(*color)  # Establece el color (por defecto, rojo).
        glLineWidth(4.0)  # Aumenta el grosor de la línea.
        glBegin(GL_LINES)
        glVertex2f(*origen)
        glVertex2f(*destino)
        glEnd()
        glFlush()

    def encontrar_nodo_mas_cercano(self, coordenadas):
        """
        Encuentra el nodo más cercano a las coordenadas dadas.
        - `coordenadas`: Coordenadas del punto (x, y).
        - Devuelve las coordenadas del nodo más cercano.
        """
        nodo_mas_cercano = None
        menor_distancia = float('inf')

        for nodo in self.nodos:
            distancia = math.hypot(coordenadas[0] - nodo[0], coordenadas[1] - nodo[1])
            if distancia < menor_distancia:
                menor_distancia = distancia
                nodo_mas_cercano = nodo

        return nodo_mas_cercano

    def encontrar_punto_en_calle(self, coordenadas):
        """
        Encuentra el punto más cercano a las coordenadas dentro de las calles (segmentos de línea).
        - `coordenadas`: Coordenadas del punto arbitrario (x, y).
        - Retorna: (punto_proyectado, segmento_calle).
        """
        punto_mas_cercano = None
        menor_distancia = float('inf')
        segmento_cercano = None

        for nombre_calle, datos_calle in Calles.items():  # Itera por las calles en el diccionario.
            origen = datos_calle["origen"]
            destino = datos_calle["destino"]

            # Proyectar el punto en la línea (segmento).
            dx, dy = destino[0] - origen[0], destino[1] - origen[1]
            if dx == 0 and dy == 0:  # Evitar división por cero.
                continue

            t = max(0, min(1, ((coordenadas[0] - origen[0]) * dx + (coordenadas[1] - origen[1]) * dy) / (
                        dx * dx + dy * dy)))
            punto_proyectado = (origen[0] + t * dx, origen[1] + t * dy)

            # Calcular la distancia al punto proyectado.
            distancia = math.hypot(punto_proyectado[0] - coordenadas[0], punto_proyectado[1] - coordenadas[1])

            if distancia < menor_distancia:
                menor_distancia = distancia
                punto_mas_cercano = punto_proyectado
                segmento_cercano = (origen, destino)

        return punto_mas_cercano, segmento_cercano
