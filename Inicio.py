# Inicio.py

from OpenGL.GLUT import *
from OpenGL.GL import *
from OpenGL.GLU import *

class Inicio:
    def __init__(self):
        # Dimensiones de la ventana
        self.width = 800
        self.height = 600
        # Definir los botones del menú
        self.botones = [
            {'label': 'Vendedor', 'x': 350, 'y': 300, 'width': 100, 'height': 50, 'action': self.modo_vendedor},
            {'label': 'Cliente', 'x': 350, 'y': 200, 'width': 100, 'height': 50, 'action': self.modo_cliente}
        ]
        self.iniciar_glut()

    def iniciar_glut(self):
        # Inicializar GLUT
        glutInit()
        glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)
        glutInitWindowSize(self.width, self.height)
        glutInitWindowPosition(100, 100)
        glutCreateWindow(b"Menu Principal")
        self.inicializar_opengl()
        glutDisplayFunc(self.display)
        glutMouseFunc(self.mouse_click)
        glutMainLoop()

    def inicializar_opengl(self):
        # Configuraciones de OpenGL
        glClearColor(1.0, 1.0, 1.0, 1.0)  # Fondo blanco
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        gluOrtho2D(0, self.width, 0, self.height)
        glMatrixMode(GL_MODELVIEW)
        glLoadIdentity()

    def display(self):
        glClear(GL_COLOR_BUFFER_BIT)
        # Dibujar botones
        for boton in self.botones:
            self.dibujar_boton(boton)
        glFlush()

    def dibujar_boton(self, boton):
        x = boton['x']
        y = boton['y']
        w = boton['width']
        h = boton['height']
        label = boton['label']

        # Dibujar el rectángulo del botón
        glColor3f(0.7, 0.7, 0.7)  # Color gris
        glBegin(GL_QUADS)
        glVertex2f(x, y)
        glVertex2f(x + w, y)
        glVertex2f(x + w, y + h)
        glVertex2f(x, y + h)
        glEnd()

        # Dibujar la etiqueta del botón
        glColor3f(0, 0, 0)  # Color negro
        self.dibujar_texto(label, x + w / 2, y + h / 2)

    def dibujar_texto(self, texto, x, y):
        # Posicionar el texto
        glRasterPos2f(x - (len(texto) * 4.5), y - 4)  # Centrado aproximado
        for ch in texto:
            glutBitmapCharacter(GLUT_BITMAP_HELVETICA_18, ord(ch))

    def mouse_click(self, button, state, x, y):
        if state == GLUT_DOWN and button == GLUT_LEFT_BUTTON:
            # Invertir coordenada y
            y = self.height - y
            for btn in self.botones:
                if (x >= btn['x'] and x <= btn['x'] + btn['width'] and
                    y >= btn['y'] and y <= btn['y'] + btn['height']):
                    # Se hizo clic en el botón
                    btn['action']()
                    break

    def modo_vendedor(self):
        # Entrar en modo vendedor
        print("Modo Vendedor seleccionado")
        from GestorVentas import GestorVentas
        gestor = GestorVentas('vendedor')
        glutDestroyWindow(glutGetWindow())  # Cerrar ventana del menú
        gestor.run()

    def modo_cliente(self):
        # Entrar en modo cliente
        print("Modo Cliente seleccionado")
        from GestorVentas import GestorVentas
        gestor = GestorVentas('cliente')
        glutDestroyWindow(glutGetWindow())  # Cerrar ventana del menú
        gestor.run()

if __name__ == "__main__":
    inicio = Inicio()
