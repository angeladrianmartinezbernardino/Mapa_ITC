import json
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
        Selecciona un punto según su tipo.
        - Los negocios se asignan como origen.
        - Las casas se asignan como destino.
        """
        punto_cercano = self.obtener_punto_cercano(x, y)
        if punto_cercano:
            if self.modo == 'vendedor' and punto_cercano['tipo'] == 'negocio':
                if not self.entrega_activa:
                    self.origen = punto_cercano
                    print(f"Origen seleccionado: {self.origen}")
            elif self.modo == 'cliente' and punto_cercano['tipo'] == 'casa':
                if self.origen:
                    self.destino = punto_cercano
                    print(f"Destino seleccionado: {self.destino}")
                    self.simular_entrega()

    def simular_entrega(self):
        """
        Simula la entrega del negocio a la casa.
        - Encuentra el camino más corto.
        - Simula la visualización del recorrido.
        """
        if not self.origen or not self.destino:
            print("Se requiere un origen y un destino para iniciar la entrega.")
            return

        self.entrega_activa = True
        camino = self.mapa.encontrar_camino_mas_corto(self.origen['coords'], self.destino['coords'])

        if not camino:
            print("No se encontró un camino válido.")
        else:
            print(f"Camino encontrado: {camino}")
            for i in range(len(camino) - 1):
                self.mapa.resaltar_calle(camino[i], camino[i + 1])

        self.origen = None
        self.destino = None
        self.entrega_activa = False
        glutPostRedisplay()

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

    def crear_menus(self):
        """Crea el menú contextual según el estado actual."""
        menu = glutCreateMenu(self.accion_menu)

        # Opciones del menú basadas en el contexto.
        if self.origen is None:
            glutAddMenuEntry("Seleccionar Punto de Origen", 1)
        elif self.destino is None:
            glutAddMenuEntry("Seleccionar Punto de Destino", 2)

        glutAttachMenu(GLUT_RIGHT_BUTTON)

    def accion_menu(self, opcion):
        """Acción según el menú seleccionado."""
        if opcion == 1:
            print("Haz clic en un negocio para seleccionar como punto de origen.")
            # Aquí puedes agregar más lógica si es necesario.
        elif opcion == 2:
            print("Haz clic en una casa para seleccionar como punto de destino.")
            # Aquí puedes agregar más lógica si es necesario.

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

if __name__ == "__main__":
    modo = input("Ingrese el modo ('vendedor' o 'cliente'): ").strip()
    gestor = GestorVentas(modo)
    gestor.run()
