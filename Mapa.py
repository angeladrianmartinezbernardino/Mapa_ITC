# En Mapa.py
from OpenGL.GL import *
from OpenGL.GLU import *
from Configuracion_Mapa import Calles
import math
import heapq

class Mapa:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grafo = {}  # Diccionario para almacenar el grafo
        self.crear_grafo()

    def crear_grafo(self):
        """Crea un grafo a partir de las calles."""
        self.nodos = {}
        node_id = 0

        for calle in Calles.values():
            origen = calle["origen"]
            destino = calle["destino"]

            # Asignar IDs únicos a los nodos
            if origen not in self.nodos:
                self.nodos[origen] = node_id
                node_id += 1
            if destino not in self.nodos:
                self.nodos[destino] = node_id
                node_id += 1

            origen_id = self.nodos[origen]
            destino_id = self.nodos[destino]

            # Calcular la distancia (peso) entre los nodos
            distancia = math.hypot(destino[0] - origen[0], destino[1] - origen[1])

            # Agregar aristas al grafo (no dirigido)
            self.grafo.setdefault(origen_id, []).append((destino_id, distancia))
            self.grafo.setdefault(destino_id, []).append((origen_id, distancia))

    def inicializar_opengl(self):
        """Inicializa las configuraciones de OpenGL."""
        glClearColor(1.0, 1.0, 1.0, 1.0)  # Fondo blanco.
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
        glClear(GL_COLOR_BUFFER_BIT)  # Limpia la pantalla
        self.dibujar_calles()  # Dibuja las calles
        self.dibujar_intersecciones()  # Dibuja las intersecciones
        glFlush()  # Asegura que se renderice el contenido.

    def encontrar_camino_mas_corto(self, origen_coord, destino_coord):
        """Encuentra el camino más corto entre dos coordenadas."""
        origen_id = self.nodos.get(origen_coord)
        destino_id = self.nodos.get(destino_coord)
        if origen_id is None or destino_id is None:
            print("Origen o destino no existen en el mapa.")
            return []

        # Implementación del algoritmo de Dijkstra
        cola = [(0, origen_id, [])]
        visitados = set()

        while cola:
            (costo, nodo_actual, camino) = heapq.heappop(cola)
            if nodo_actual in visitados:
                continue

            visitados.add(nodo_actual)
            camino = camino + [nodo_actual]

            if nodo_actual == destino_id:
                # Convertir IDs de nodos a coordenadas
                camino_coords = [list(self.nodos.keys())[list(self.nodos.values()).index(n)] for n in camino]
                return camino_coords

            for vecino, peso in self.grafo.get(nodo_actual, []):
                if vecino not in visitados:
                    heapq.heappush(cola, (costo + peso, vecino, camino))

        print("No se encontró un camino.")
        return []
