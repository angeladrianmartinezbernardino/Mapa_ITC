# GestorVentas.py

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *
from Mapa import Mapa

class GestorVentas:
    def __init__(self, modo):
        self.modo = modo  # 'vendedor' o 'cliente'
        self.width = 1200
        self.height = 600
        self.mapa = Mapa(self.width, self.height)
        self.puntos = []  # Lista de puntos (casas y negocios)
        self.punto_seleccionado = None
        self.ultima_posicion_click = None

    def run(self):
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        if self.modo == 'vendedor':
            glutCreateWindow(b"Modo Vendedor - Gestion de Ventas")
        else:
            glutCreateWindow(b"Modo Cliente - Realizar Pedido")
        self.inicializar_opengl()
        self.crear_menus()
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse_click)
        glutMainLoop()

    def inicializar_opengl(self):
        self.mapa.inicializar_opengl()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        self.mapa.display()
        # Dibujar puntos adicionales (casas y negocios)
        self.dibujar_puntos()
        glFlush()

    def dibujar_puntos(self):
        for punto in self.puntos:
            x, y = punto['coords']
            if punto['tipo'] == 'casa':
                glColor3f(0, 0, 1)  # Azul para casas
            elif punto['tipo'] == 'negocio':
                glColor3f(0, 1, 0)  # Verde para negocios
            glPointSize(10)
            glBegin(GL_POINTS)
            glVertex2f(x, y)
            glEnd()

    def mouse_click(self, button, state, x, y):
        if state == GLUT_DOWN:
            # Invertir coordenada y
            y = self.height - y
            self.ultima_posicion_click = (x, y)
            if button == GLUT_RIGHT_BUTTON:
                # Clic derecho: seleccionar punto
                self.seleccionar_punto(x, y)
            # El menú está asociado al clic izquierdo

    def seleccionar_punto(self, x, y):
        for punto in self.puntos:
            px, py = punto['coords']
            if abs(px - x) < 10 and abs(py - y) < 10:
                self.punto_seleccionado = punto
                print(f"Punto seleccionado en ({px}, {py})")
                return
        self.punto_seleccionado = None
        print("No se seleccionó ningún punto")

    def crear_menus(self):
        if self.modo == 'vendedor':
            # Crear menú para el vendedor
            submenu = glutCreateMenu(self.accion_menu)
            glutAddMenuEntry("Agregar Negocio", 1)
            glutAddMenuEntry("Agregar Casa", 2)
            glutAddMenuEntry("Eliminar Punto", 3)
            glutAttachMenu(GLUT_LEFT_BUTTON)
        elif self.modo == 'cliente':
            # Crear menú para el cliente
            submenu = glutCreateMenu(self.accion_menu)
            glutAddMenuEntry("Establecer Ubicación de Casa", 4)
            glutAttachMenu(GLUT_LEFT_BUTTON)

    def accion_menu(self, opcion):
        if opcion == 1:
            # Agregar negocio en la última posición clickeada
            if self.ultima_posicion_click:
                x, y = self.ultima_posicion_click
                self.puntos.append({'coords': (x, y), 'tipo': 'negocio'})
                glutPostRedisplay()
        elif opcion == 2:
            # Agregar casa en la última posición clickeada
            if self.ultima_posicion_click:
                x, y = self.ultima_posicion_click
                self.puntos.append({'coords': (x, y), 'tipo': 'casa'})
                glutPostRedisplay()
        elif opcion == 3:
            # Eliminar punto seleccionado
            self.eliminar_punto()
        elif opcion == 4:
            # El cliente establece su ubicación de casa
            if self.ultima_posicion_click:
                x, y = self.ultima_posicion_click
                self.puntos.append({'coords': (x, y), 'tipo': 'casa'})
                glutPostRedisplay()

    def eliminar_punto(self):
        if self.punto_seleccionado:
            self.puntos.remove(self.punto_seleccionado)
            self.punto_seleccionado = None
            glutPostRedisplay()
