import json
from OpenGL.GLUT import *
from OpenGL.GL import *
from Mapa import Mapa

class GestorVentas:
    def __init__(self, modo):
        self.modo = modo  # 'vendedor' o 'cliente'.
        self.width = 1200
        self.height = 600
        self.mapa = Mapa(self.width, self.height)
        self.puntos = []  # Lista de puntos en el mapa.
        self.registro_archivo = "acciones_mapa.json"  # Archivo para guardar las acciones.
        self.punto_seleccionado = None
        self.seleccionando_destino = False
        self.cargar_registro()

    def cargar_registro(self):
        """Carga el registro de acciones previas desde un archivo."""
        try:
            with open(self.registro_archivo, 'r') as archivo:
                self.puntos = json.load(archivo)
        except FileNotFoundError:
            self.puntos = []

    def guardar_registro(self):
        """Guarda el registro actual de puntos en un archivo."""
        with open(self.registro_archivo, 'w') as archivo:
            json.dump(self.puntos, archivo)

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

    def mouse_click(self, button, state, x, y):
        """Manejador de eventos de clic."""
        if state == GLUT_DOWN:
            y = self.height - y
            if button == GLUT_LEFT_BUTTON:
                self.agregar_punto(x, y, 'negocio' if self.modo == 'vendedor' else 'casa')
            elif button == GLUT_RIGHT_BUTTON:
                self.eliminar_punto(x, y)

    def agregar_punto(self, x, y, tipo):
        """Agrega un nuevo punto en el mapa."""
        self.puntos.append({'coords': (x, y), 'tipo': tipo})
        self.guardar_registro()
        glutPostRedisplay()

    def eliminar_punto(self, x, y):
        """Elimina un punto del mapa."""
        for punto in self.puntos:
            px, py = punto['coords']
            if abs(px - x) < 10 and abs(py - y) < 10:
                self.puntos.remove(punto)
                self.guardar_registro()
                glutPostRedisplay()
                return

    def crear_menus(self):
        """Crea los menús para las acciones."""
        menu = glutCreateMenu(self.accion_menu)
        glutAddMenuEntry("Agregar Negocio (Clic Izq.)", 1)
        glutAddMenuEntry("Eliminar Punto (Clic Der.)", 2)
        glutAttachMenu(GLUT_RIGHT_BUTTON)

    def accion_menu(self, opcion):
        """Manejador de acciones del menú."""
        if opcion == 1:
            print("Usa clic izquierdo para agregar un negocio o casa.")
        elif opcion == 2:
            print("Usa clic derecho para eliminar un punto.")

    def cerrar_ventana(self):
        """Valida y cierra la ventana."""
        print("Guardando datos antes de salir...")
        self.guardar_registro()
        glutLeaveMainLoop()

    def run(self):
        """Ejecuta la ventana principal de GLUT."""
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        titulo = b"Modo Vendedor" if self.modo == 'vendedor' else b"Modo Cliente"
        glutCreateWindow(titulo)
        self.inicializar_opengl()
        self.crear_menus()
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse_click)
        glutWMCloseFunc(self.cerrar_ventana)
        glutMainLoop()
