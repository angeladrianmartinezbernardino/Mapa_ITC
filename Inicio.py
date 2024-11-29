from OpenGL.GLUT import *
from Mapa import Mapa

# Dimensiones de la ventana.
Eje_X = 1200
Eje_Y = 600

def main():
    # Crear instancia de la clase Mapa.
    mapa = Mapa(Eje_X, Eje_Y)

    # Inicializar GLUT
    glutInit()
    glutInitDisplayMode(GLUT_SINGLE | GLUT_RGB)  # Modo de display.
    glutInitWindowSize(Eje_X, Eje_Y)  # Tamaño de la ventana.
    glutInitWindowPosition(100, 100)  # Posición de la ventana.
    glutCreateWindow(b"Mapa de Calles e Intersecciones")  # Crear ventana.

    # Inicializar OpenGL.
    mapa.inicializar_opengl()

    # Configurar función de display.
    glutDisplayFunc(mapa.display)

    # Iniciar bucle principal de GLUT.
    glutMainLoop()

if __name__ == "__main__":
    main()
