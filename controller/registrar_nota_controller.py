from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.menu import MDDropdownMenu
from kivymd.app import MDApp

class RegistrarNotaScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        
        self.id_estudiante_sel = None
        self.codigo_materia_sel = None
        
        # Lista en memoria para rastrear los TextFields creados dinámicamente
        self.campos_dinamicos = [] 
        # Límite máximo permitido de slots nuevos para el alumno seleccionado
        self.slots_disponibles = 0 

    def abrir_menu_estudiantes(self, boton_llamador):
        alumnos_bd = self.app.student.consultar_estudiantes() 
        opciones = [
            {
                "text": f"{fila[2]} (ID: {fila[0]})",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=fila[0], y=fila[2]: self.asignar_estudiante(x, y),
            }
            for fila in alumnos_bd
        ]
        self.menu_estudiantes = MDDropdownMenu(caller=boton_llamador, items=opciones, width_mult=4)
        self.menu_estudiantes.open()

    def asignar_estudiante(self, id_est, nombre_est):
        self.id_estudiante_sel = id_est
        self.ids.btn_estudiante.text = f"Estudiante: {nombre_est}"
        self.menu_estudiantes.dismiss()
        self.verificar_y_preparar_formulario() # Comprobar estado al seleccionar

    def abrir_menu_materias(self, boton_llamador):
        materias_bd = self.app.materia.consultar_materias() 
        opciones = [
            {
                "text": f"{fila[1]} (Código: {fila[0]})",
                "viewclass": "OneLineListItem",
                "on_release": lambda x=fila[0], y=fila[1]: self.asignar_materia(x, y),
            }
            for fila in materias_bd
        ]
        self.menu_materias = MDDropdownMenu(caller=boton_llamador, items=opciones, width_mult=4)
        self.menu_materias.open()

    def asignar_materia(self, cod_mat, nombre_mat):
        self.codigo_materia_sel = cod_mat
        self.ids.btn_materia.text = f"Materia: {nombre_mat}"
        self.menu_materias.dismiss()
        self.verificar_y_preparar_formulario() # Comprobar estado al seleccionar

    def verificar_y_preparar_formulario(self):
        """Calcula cuántas notas ya existen en la DB y reinicia los inputs dinámicos"""
        if not self.id_estudiante_sel or not self.codigo_materia_sel:
            return # Necesitamos ambas selecciones primero
            
        # Limpiamos lo que haya en pantalla de consultas previas
        self.ids.contenedor_inputs.clear_widgets()
        self.campos_dinamicos.clear()
        
        # Consultamos cuántas notas reales ya existen en SQLite
        notas_existentes = self.app.nota.contar_notas_estudiante(self.id_estudiante_sel, self.codigo_materia_sel)
        self.slots_disponibles = 5 - notas_existentes
        
        if self.slots_disponibles <= 0:
            print("¡Error! Este alumno ya tiene las 5 notas reglamentarias en la Base de Datos.")
            self.ocultar_boton_mas()
            return
            
        # Agregamos automáticamente la primera fila para empezar a escribir
        self.agregar_fila_formulario()

    def agregar_fila_formulario(self):
        """Inyecta una fila horizontal con campos de Nota y Fecha en la interfaz"""
        # Validamos si agregar esta fila nos haría pasar del límite de 5
        cant_actual_en_pantalla = len(self.campos_dinamicos)
        
        if cant_actual_en_pantalla >= self.slots_disponibles:
            print("No puedes añadir más filas. Límite de 5 alcanzado.")
            return

        # Creación de la fila contenedora horizontal
        fila_layout = MDBoxLayout(orientation='horizontal', spacing="12dp", adaptive_height=True)
        
        # Input de Nota
        txt_nota = MDTextField(hint_text=f"Nota #{cant_actual_en_pantalla + 1}", input_filter="float", size_hint_x=0.4)
        # Input de Fecha
        txt_fecha = MDTextField(hint_text="Fecha (AAAA-MM-DD)", size_hint_x=0.6)
        
        # Metemos los inputs en la fila horizontal
        fila_layout.add_widget(txt_nota)
        fila_layout.add_widget(txt_fecha)
        
        # Inyectamos la fila completa en el contenedor vertical de la vista (.kv)
        self.ids.contenedor_inputs.add_widget(fila_layout)
        
        # Guardamos la referencia de los inputs en nuestra lista de control
        self.campos_dinamicos.append({"nota_field": txt_nota, "fecha_field": txt_fecha})
        
        # Control del boton "+": 
        # Si con esta fila ya alcanzamos las 5 notas en total, escondemos el botón "+" de inmediato
        if len(self.campos_dinamicos) == self.slots_disponibles:
            self.ocultar_boton_mas()
        else:
            self.mostrar_boton_mas()

    def mostrar_boton_mas(self):
        """Hace visible y funcional el botón '+'"""
        btn = self.ids.btn_agregar_fila
        btn.opacity = 1
        btn.disabled = False
        btn.height = "48dp"
        btn.size_hint_y = None

    def ocultar_boton_mas(self):
        """Desaparece por completo el botón '+' sin dejar espacios vacíos"""
        btn = self.ids.btn_agregar_fila
        btn.opacity = 0
        btn.disabled = True
        btn.height = 0
        btn.size_hint_y = None

    def guardar_todas_las_notas(self):
        if not self.id_estudiante_sel or not self.codigo_materia_sel:
            print("Error: Selecciona estudiante y materia.")
            return
            
        if not self.campos_dinamicos:
            print("Error: No hay notas para registrar.")
            return

        id_profesor = self.app.sesion_usuario["id_usuario"]
        
        # Recorremos la lista de diccionarios para extraer los textos reales escritos por el usuario
        for fila in self.campos_dinamicos:
            nota_texto = fila["nota_field"].text
            fecha_texto = fila["fecha_field"].text
            
            if not nota_texto or not fecha_texto:
                print("¡Error! Tienes filas vacías en el formulario.")
                return
                
            # Guardamos cada registro de forma real e independiente en SQLite
            self.app.nota.registrar_notas(
                id_estudiante=self.id_estudiante_sel,
                id_usuario=int(id_profesor),
                nota=float(nota_texto),
                fecha_evaluacion=fecha_texto,
                codigo_materia=self.codigo_materia_sel
            )
            
        print("¡Todas las calificaciones fueron insertadas con éxito!")
        self.limpiar_formulario()
        self.regresar()

    def limpiar_formulario(self):
        self.id_estudiante_sel = None
        self.codigo_materia_sel = None
        self.ids.btn_estudiante.text = "Seleccionar Estudiante"
        self.ids.btn_materia.text = "Seleccionar Materia"
        self.ids.contenedor_inputs.clear_widgets()
        self.campos_dinamicos.clear()
        self.ocultar_boton_mas()

    def regresar(self):
        self.manager.transition.direction = "right"
        self.manager.current = "pantalla_notas"
