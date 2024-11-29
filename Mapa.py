from OpenGL.GL import *
from OpenGL.GLU import *
from Configuracion_Mapa import Calles

class Mapa:
    def __init__(self, width, height):
        self.width = width
        self.height = height

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
