import json
import math
from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Mapa import Mapa  # Importar la clase del mapa ya definida.

class GestorVentas:
    def __init__(self, modo):
        """
        Inicializa el gestor de ventas.
        - `modo`: 'vendedor' o 'cliente', determina las acciones permitidas.
        """
        self.modo = modo
        self.width = 900
        self.height = 600
        self.mapa = Mapa(self.width, self.height)
        self.puntos = []  # Lista de puntos en el mapa.
        self.origen = None  # Punto de origen (solo negocios).
        self.destino = None  # Punto de destino (solo casas).
        self.entrega_activa = False  # Estado de la simulación.
        self.registro_archivo = "acciones_mapa.json"  # Archivo de persistencia.
        self.cargar_registro()

    def cargar_registro(self):
        """Carga puntos almacenados previamente desde un archivo JSON."""
        try:
            with open(self.registro_archivo, 'r') as archivo:
                self.puntos = json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.puntos = []

    def guardar_registro(self):
        """Guarda los puntos actuales en el archivo JSON."""
        with open(self.registro_archivo, 'w') as archivo:
            json.dump(self.puntos, archivo, indent=4)

    def inicializar_opengl(self):
        """Configura OpenGL para la ventana gráfica."""
        self.mapa.inicializar_opengl()

    def display(self):
        """Función de dibujo principal."""
        glClear(GL_COLOR_BUFFER_BIT)
        self.mapa.display()
        self.dibujar_puntos()
        glFlush()

    def dibujar_puntos(self):
        """Dibuja todos los puntos del mapa."""
        for punto in self.puntos:
            x, y = punto['coords']
            if punto['tipo'] == 'casa':
                glColor3f(0, 0, 1)  # Azul para casas.
            elif punto['tipo'] == 'negocio':
                glColor3f(0, 1, 0)  # Verde para negocios.
            glPointSize(10)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()

    def seleccionar_punto(self, x, y):
        """
        Selecciona un punto según su tipo:
        - Negocios como origen.
        - Casas como destino.
        """
        if self.entrega_activa:  # Bloquear interacciones si la entrega está activa.
            print("Entrega en curso. No se pueden seleccionar más puntos.")
            return

        punto_cercano = self.obtener_punto_cercano(x, y)
        if punto_cercano:
            if self.origen is None and punto_cercano['tipo'] == 'negocio':
                self.origen = punto_cercano
                print(f"Origen seleccionado: {self.origen}")
            elif self.destino is None and punto_cercano['tipo'] == 'casa':
                self.destino = punto_cercano
                print(f"Destino seleccionado: {self.destino}")
                self.simular_entrega()

    def simular_entrega(self):
        """
        Simula la entrega del negocio a la casa.
        - Encuentra el camino más corto.
        - Simula la visualización del recorrido progresivo.
        """
        if not self.origen or not self.destino:
            print("Se requiere un origen y un destino para iniciar la entrega.")
            return

        # Encuentra los nodos más cercanos en el grafo para el origen y destino.
        nodo_origen = self.mapa.encontrar_nodo_mas_cercano(self.origen['coords'])
        nodo_destino = self.mapa.encontrar_nodo_mas_cercano(self.destino['coords'])

        if nodo_origen is None or nodo_destino is None:
            print("No se encontraron nodos cercanos al origen o destino.")
            self.resetear_entrega()
            return

        print(f"Nodo de origen: {nodo_origen}, Nodo de destino: {nodo_destino}")

        # Encuentra el camino más corto.
        camino = self.mapa.encontrar_camino_mas_corto(nodo_origen, nodo_destino)

        if not camino:
            print("No se encontró un camino válido.")
            self.resetear_entrega()
            return

        # Guarda el camino en un atributo para usarlo posteriormente.
        self.camino = camino
        print(f"Camino encontrado: {camino}")
        self.animar_recorrido(camino)

    def animar_recorrido(self, camino, indice=0, progreso=0):
        """
        Anima el recorrido desde el origen al destino, llenando el camino progresivamente.
        - `camino`: Lista de nodos (coordenadas) que forman la ruta.
        - `indice`: Índice del nodo actual que se está procesando.
        - `progreso`: Progreso dentro del segmento actual en píxeles.
        """
        if indice < len(camino) - 1:
            origen = camino[indice]
            destino = camino[indice + 1]

            # Calcula la distancia total entre los nodos.
            distancia_total = math.hypot(destino[0] - origen[0], destino[1] - origen[1])

            # Calcula el progreso actual como una fracción del segmento.
            fraccion = progreso / distancia_total if distancia_total > 0 else 1.0
            x_actual = origen[0] + fraccion * (destino[0] - origen[0])
            y_actual = origen[1] + fraccion * (destino[1] - origen[1])

            # Dibuja la línea hasta el progreso actual.
            glColor3f(1, 0, 0)  # Rojo para la animación.
            glLineWidth(4.0)  # Línea gruesa para destacar.
            glBegin(GL_LINES)
            glVertex2f(origen[0], origen[1])
            glVertex2f(x_actual, y_actual)
            glEnd()
            glFlush()

            # Si no se ha completado el segmento, avanza en 1 píxel.
            if progreso < distancia_total:
                glutTimerFunc(100, lambda value: self.animar_recorrido(camino, indice, progreso + 1), 0)
            else:
                # Avanza al siguiente segmento.
                glutTimerFunc(100, lambda value: self.animar_recorrido(camino, indice + 1, 0), 0)
        else:
            print("Simulación de entrega completada.")
            self.resetear_entrega()

    def resetear_entrega(self):
        """
        Reinicia el estado de la entrega y muestra los resultados.
        """
        # Calcular la distancia total del camino.
        if hasattr(self, 'camino') and self.camino:
            distancia_total = 0
            for i in range(len(self.camino) - 1):
                nodo_origen = self.camino[i]
                nodo_destino = self.camino[i + 1]
                distancia_total += math.hypot(
                    nodo_destino[0] - nodo_origen[0],
                    nodo_destino[1] - nodo_origen[1]
                )

            # Mostrar la ventana de resultados.
            self.mostrar_resultado(distancia_total)

        # Reiniciar el estado.
        self.entrega_activa = False
        self.origen = None
        self.destino = None
        self.camino = []  # Limpia el atributo camino.
        glutPostRedisplay()

    def mouse_click(self, button, state, x, y):
        """
        Manejador de clics del ratón.
        - Bloquea interacciones si hay una entrega activa.
        """
        if self.entrega_activa:  # Bloquear interacciones si la entrega está activa.
            print("Entrega en curso. No se permiten interacciones.")
            return

        if state == GLUT_DOWN:
            y = self.height - y  # Ajustar coordenada Y.
            if button == GLUT_LEFT_BUTTON:
                punto_cercano = self.obtener_punto_cercano(x, y)
                if punto_cercano:
                    self.seleccionar_punto(x, y)
                else:
                    nuevo_tipo = 'negocio' if self.modo == 'vendedor' else 'casa'
                    self.agregar_punto(x, y, nuevo_tipo)
            elif button == GLUT_RIGHT_BUTTON:
                self.crear_menus()  # Actualiza el menú dinámicamente.

    def obtener_punto_cercano(self, x, y):
        """Devuelve el punto más cercano a las coordenadas dadas."""
        for punto in self.puntos:
            px, py = punto['coords']
            if abs(px - x) <= 10 and abs(py - y) <= 10:
                return punto
        return None

    def agregar_punto(self, x, y, tipo):
        """
        Agrega un nuevo punto al mapa.
        - `tipo`: 'casa' o 'negocio'.
        """
        nuevo_punto = {'coords': [x, y], 'tipo': tipo}
        self.puntos.append(nuevo_punto)
        self.guardar_registro()
        print(f"Nuevo punto agregado: {nuevo_punto}")
        glutPostRedisplay()

    def mouse_click(self, button, state, x, y):
        """Manejador de clics del ratón."""
        if self.entrega_activa:  # Bloquear interacciones si la entrega está activa.
            print("Entrega en curso. No se permiten interacciones.")
            return

        if state == GLUT_DOWN:
            y = self.height - y  # Ajustar coordenada Y.
            punto_cercano = self.obtener_punto_cercano(x, y)

            if button == GLUT_LEFT_BUTTON:  # Clic izquierdo.
                if punto_cercano:
                    self.seleccionar_punto(x, y)
                else:
                    nuevo_tipo = 'negocio' if self.modo == 'vendedor' else 'casa'
                    self.agregar_punto(x, y, nuevo_tipo)

            elif button == GLUT_RIGHT_BUTTON:  # Clic derecho.
                if punto_cercano:  # Solo activa el menú si hay un punto cercano.
                    self.crear_menus()  # Actualiza el menú dinámicamente.
                else:
                    print("No hay puntos cercanos para interactuar.")

    def crear_menus(self):
        """Crea el menú contextual dinámicamente según el estado actual."""
        # Elimina el menú previo para evitar conflictos.
        glutDetachMenu(GLUT_RIGHT_BUTTON)
        menu = glutCreateMenu(self.accion_menu)

        # Si no hay origen definido, solo permite seleccionar origen.
        if self.origen is None:
            glutAddMenuEntry("Seleccionar Punto de Origen", 1)

        # Si ya hay origen y no hay destino definido, permite seleccionar destino.
        elif self.destino is None:
            glutAddMenuEntry("Seleccionar Punto de Destino", 2)

        glutAttachMenu(GLUT_RIGHT_BUTTON)

    def accion_menu(self, opcion):
        """Acción según el menú seleccionado."""
        if opcion == 1 and self.origen is None:
            print("Haz clic en un negocio para seleccionar como punto de origen.")
        elif opcion == 2 and self.destino is None:
            print("Haz clic en una casa para seleccionar como punto de destino.")
        else:
            print("Acción inválida o ya completada.")
        return 0  # Devuelve un valor entero explícito para GLUT.

    def run(self):
        """Ejecuta la ventana principal del gestor."""
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(b"Gestor de Ventas")
        self.inicializar_opengl()
        self.crear_menus()
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse_click)
        glutMainLoop()

    def mostrar_resultado(self, distancia_total):
        """
        Muestra una ventana con el resultado del recorrido.
        - `distancia_total`: Distancia total recorrida en píxeles.
        """
        tiempo_total = distancia_total * 0.1  # Tiempo en segundos.
        tarifa = distancia_total * 5  # Tarifa en pesos mexicanos.

        def inicializar_ventana():
            # Inicializa la ventana de OpenGL.
            glutInit()
            glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
            glutInitWindowSize(400, 300)
            glutInitWindowPosition(100, 100)
            glutCreateWindow(b"Resultado de la Entrega")
            glClearColor(1.0, 1.0, 1.0, 1.0)  # Fondo blanco.
            gluOrtho2D(0, 400, 0, 300)  # Coordenadas 2D.
            glutDisplayFunc(renderizar_resultado)
            glutMainLoop()

        def renderizar_resultado():
            # Renderiza el texto con los resultados.
            glClear(GL_COLOR_BUFFER_BIT)
            glColor3f(0, 0, 0)  # Texto negro.

            def dibujar_texto(texto, x, y):
                glRasterPos2f(x, y)
                for ch in texto:
                    glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

            # Texto a mostrar.
            mensajes = [
                f"Distancia total recorrida: {distancia_total:.2f} pixeles",
                f"Tiempo total recorrido: {tiempo_total:.2f} segundos",
                f"Tarifa de entrega: ${tarifa:.2f} pesos",
                "Nota: Cada 1 pixel = 0.1 segundos y 5 pesos.",
                "Presiona la X para cerrar esta ventana."
            ]

            y = 250  # Posición inicial en Y.
            for mensaje in mensajes:
                dibujar_texto(mensaje, 20, y)
                y -= 40  # Espaciado entre líneas.

            glFlush()

        # Inicializar y mostrar la ventana.
        inicializar_ventana()

if __name__ == "__main__":
    modo = input("Ingrese el modo ('vendedor' o 'cliente'): ").strip()
    gestor = GestorVentas(modo)
    gestor.run()
