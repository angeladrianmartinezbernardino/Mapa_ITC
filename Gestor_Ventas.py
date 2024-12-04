from OpenGL.GLUT import *
from OpenGL.GL import *
from Mapa import Mapa

class GestorVentas:
    def __init__(self, modo):
        self.modo = modo  # 'vendedor' o 'cliente'.
        self.width = 1200
        self.height = 600
        self.mapa = Mapa(self.width, self.height)
        self.puntos = []  # Lista de puntos (casas y negocios).
        self.punto_seleccionado = None
        self.ultima_posicion_click = None
        self.seleccionando_destino = False  # Inicializar como False.
        self.destino = None  # Inicializar como None.

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
        # Dibujar puntos adicionales (casas y negocios).
        self.dibujar_puntos()
        glFlush()

    def dibujar_puntos(self):
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

    def mouse_click(self, button, state, x, y):
        if state == GLUT_DOWN:
            y = self.height - y
            self.ultima_posicion_click = (x, y)

            if self.seleccionando_destino and button == GLUT_RIGHT_BUTTON:
                # Seleccionar casa destino
                for punto in self.puntos:
                    if punto['tipo'] == 'casa':
                        px, py = punto['coords']
                        if abs(px - x) < 10 and abs(py - y) < 10:
                            self.destino = punto
                            print(f"Destino seleccionado en ({px}, {py})")
                            self.seleccionando_destino = False
                            self.calcular_y_mostrar_ruta()
                            return
                print("Debe seleccionar una casa válida.")
                return

            if button == GLUT_RIGHT_BUTTON:
                # Seleccionar punto (para eliminar).
                self.seleccionar_punto(x, y)
            elif button == GLUT_LEFT_BUTTON:
                # Seleccionar negocio
                for punto in self.puntos:
                    px, py = punto['coords']
                    if abs(px - x) < 10 and abs(py - y) < 10:
                        if self.modo == 'vendedor' and punto['tipo'] == 'negocio':
                            for p in self.puntos:
                                p['seleccionado'] = False
                            punto['seleccionado'] = True
                            print(f"Negocio seleccionado en ({px}, {py})")
                            glutPostRedisplay()
                            return

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
            submenu = glutCreateMenu(self.accion_menu)
            glutAddMenuEntry("Agregar Negocio", 1)
            glutAddMenuEntry("Agregar Casa", 2)
            glutAddMenuEntry("Eliminar Punto", 3)
            glutAddMenuEntry("Iniciar Viaje", 5)  # Nueva opción.
            glutAttachMenu(GLUT_LEFT_BUTTON)
        elif self.modo == 'cliente':
            submenu = glutCreateMenu(self.accion_menu)
            glutAddMenuEntry("Establecer Ubicación de Casa", 4)
            glutAttachMenu(GLUT_LEFT_BUTTON)

    def accion_menu(self, opcion):
        if opcion == 1:
            # Agregar negocio en la última posición clickeada.
            if self.ultima_posicion_click:
                x, y = self.ultima_posicion_click
                self.puntos.append({'coords': (x, y), 'tipo': 'negocio'})
                glutPostRedisplay()
        elif opcion == 2:
            # Agregar casa en la última posición clickeada.
            if self.ultima_posicion_click:
                x, y = self.ultima_posicion_click
                self.puntos.append({'coords': (x, y), 'tipo': 'casa'})
                glutPostRedisplay()
        elif opcion == 3:
            # Eliminar punto seleccionado.
            self.eliminar_punto()
        elif opcion == 4:
            # El cliente establece su ubicación de casa.
            if self.ultima_posicion_click:
                x, y = self.ultima_posicion_click
                self.puntos.append({'coords': (x, y), 'tipo': 'casa'})
                glutPostRedisplay()
        elif opcion == 5:
            # Iniciar viaje
            self.iniciar_viaje()

    def eliminar_punto(self):
        if self.punto_seleccionado:
            self.puntos.remove(self.punto_seleccionado)
            self.punto_seleccionado = None
            glutPostRedisplay()

    def iniciar_viaje(self):
        if self.modo != 'vendedor':
            print("Solo los vendedores pueden iniciar un viaje.")
            return

        # Verificar si hay un negocio seleccionado.
        negocio = None
        for punto in self.puntos:
            if punto['tipo'] == 'negocio' and 'seleccionado' in punto and punto['seleccionado']:
                negocio = punto
                break

        if not negocio:
            print("Debe seleccionar un negocio para iniciar el viaje.")
            return

        print("Seleccione una casa haciendo clic derecho sobre ella.")
        self.seleccionando_destino = True

    def calcular_y_mostrar_ruta(self):
        # Obtener coordenadas del negocio y la casa seleccionados.
        origen = None
        destino = None

        for punto in self.puntos:
            if punto['tipo'] == 'negocio' and 'seleccionado' in punto and punto['seleccionado']:
                origen = punto['coords']
            if punto == self.destino:
                destino = punto['coords']

        if origen and destino:
            ruta = self.mapa.encontrar_camino_mas_corto(origen, destino)
            if ruta:
                self.ruta = ruta
                self.animar_viaje()
            else:
                print("No se pudo encontrar una ruta entre los puntos seleccionados.")
        else:
            print("No se pudo determinar el origen y destino para el viaje.")

    def animar_viaje(self):
        # Dibujar la ruta como una línea amarilla.
        def draw_route():
            self.display()
            glColor3f(1, 1, 0)  # Color amarillo.
            glLineWidth(4.0)
            glBegin(GL_LINE_STRIP)
            for x, y in self.ruta:
                glVertex2f(x, y)
            glEnd()
            glFlush()

        glutDisplayFunc(draw_route)
        glutPostRedisplay()

    # En GestorVentas.py, dentro de la clase GestorVentas.

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
        glutWMCloseFunc(self.cerrar_ventana)  # Capturamos el cierre de la ventana.
        glutMainLoop()

    def cerrar_ventana(self):
        glutLeaveMainLoop()  # Salimos del bucle de GLUT.
        # Volvemos al menú de inicio.
        Inicio()
