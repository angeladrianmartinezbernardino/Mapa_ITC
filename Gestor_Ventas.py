import json
from OpenGL.GLUT import *
from OpenGL.GL import *
from Mapa import Mapa

class GestorVentas:
    def __init__(self, modo):
        self.modo = modo  # 'vendedor' o 'cliente'.
        self.width = 900
        self.height = 600
        self.mapa = Mapa(self.width, self.height)
        self.puntos = []  # Lista de puntos en el mapa.
        self.entrega_en_curso = False  # Flag para verificar si hay una entrega en curso.
        self.punto_origen = None
        self.punto_destino = None
        self.registro_archivo = "acciones_mapa.json"
        self.cargar_registro()

    def cargar_registro(self):
        """Carga los puntos desde un archivo JSON estándar."""
        try:
            with open(self.registro_archivo, 'r') as archivo:
                self.puntos = json.load(archivo)
        except (FileNotFoundError, json.JSONDecodeError):
            self.puntos = []

    def guardar_registro(self):
        """Guarda todos los puntos en el archivo como un arreglo JSON estándar."""
        with open(self.registro_archivo, 'w') as archivo:
            json.dump(self.puntos, archivo, indent=4)

    def inicializar_opengl(self):
        """Configuración inicial de OpenGL."""
        self.mapa.inicializar_opengl()

    def display(self):
        """Función de dibujo de GLUT."""
        glClear(GL_COLOR_BUFFER_BIT)
        self.mapa.display()
        self.dibujar_puntos()
        glFlush()

    def dibujar_puntos(self):
        """Dibuja las casas y negocios en el mapa."""
        for punto in self.puntos:
            x, y = punto['coords']
            glColor3f(0, 0, 1) if punto['tipo'] == 'casa' else glColor3f(0, 1, 0)
            glPointSize(10)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()

    def seleccionar_punto(self, x, y):
        """Selecciona un punto como origen o destino."""
        if not self.punto_origen:
            self.punto_origen = (x, y)
            print(f"Punto de origen seleccionado: {self.punto_origen}")
        elif not self.punto_destino:
            self.punto_destino = (x, y)
            print(f"Punto de destino seleccionado: {self.punto_destino}")
            self.simular_entrega()

    def simular_entrega(self):
        """Simula la entrega resaltando el camino más corto."""
        if self.entrega_en_curso or not self.punto_origen or not self.punto_destino:
            print("Entrega no iniciada: Verifica que el origen y destino estén definidos y no haya entregas en curso.")
            return

        self.entrega_en_curso = True
        camino = self.mapa.encontrar_camino_mas_corto(self.punto_origen, self.punto_destino)

        if not camino:
            print("No se encontró un camino válido.")
            self.resetear_entrega()
            return

        # Resaltar las calles del camino.
        for i in range(len(camino) - 1):
            self.mapa.resaltar_calle(camino[i], camino[i + 1])

        print("Simulación de entrega completada.")
        self.resetear_entrega()

    def resetear_entrega(self):
        """Reinicia el estado de la entrega."""
        self.entrega_en_curso = False
        self.punto_origen = None
        self.punto_destino = None
        glutPostRedisplay()

    def mouse_click(self, button, state, x, y):
        """Manejador de eventos de clic."""
        if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
            y = self.height - y  # Ajustar coordenada Y.
            punto_existente = self.obtener_punto_cercano(x, y)

            if punto_existente:
                # Descomponer las coordenadas del punto existente.
                px, py = punto_existente['coords']
                self.seleccionar_punto(px, py)
            else:
                # Agregar un nuevo punto si no existe uno cercano.
                nuevo_tipo = 'negocio' if self.modo == 'vendedor' else 'casa'
                self.agregar_punto(x, y, nuevo_tipo)

    def obtener_punto_cercano(self, x, y):
        """Busca un punto cercano a las coordenadas dadas."""
        for punto in self.puntos:
            px, py = punto['coords']
            if abs(px - x) <= 10 and abs(py - y) <= 10:
                return punto
        return None

    def agregar_punto(self, x, y, tipo):
        """Agrega un nuevo punto al mapa."""
        nuevo_punto = {'coords': [x, y], 'tipo': tipo}
        self.puntos.append(nuevo_punto)
        self.guardar_registro()
        print(f"Nuevo punto agregado: {nuevo_punto}")
        glutPostRedisplay()

    def crear_menus(self):
        """Crea los menús para las acciones."""
        # Define las opciones del menú
        menu = glutCreateMenu(self.accion_menu)
        glutAddMenuEntry("Seleccionar Punto de Origen", 1)
        glutAddMenuEntry("Seleccionar Punto de Destino", 2)
        glutAttachMenu(GLUT_RIGHT_BUTTON)

    def accion_menu(self, opcion):
        """Manejador de acciones del menú."""
        if opcion == 1:
            print("Haz clic izquierdo para seleccionar el punto de origen.")
        elif opcion == 2:
            print("Haz clic izquierdo para seleccionar el punto de destino.")
        return 0  # Asegura que devuelves un entero al finalizar

    def run(self):
        """Ejecuta la ventana principal de GLUT."""
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        titulo = b"Simulacion de Entrega"
        glutCreateWindow(titulo)
        self.inicializar_opengl()
        self.crear_menus()
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse_click)
        glutMainLoop()  # Aquí se asegura que GLUT procesa correctamente
