from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.list import TwoLineAvatarIconListItem, IconRightWidget, IconLeftWidget

class StudentView(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs) 
        # Memoria para identificar si es un registro nuevo o actualización
        self.id_estudiante_a_editar = None
    
    def on_kv_post(self, base_widget):
        """Se ejecuta automáticamente al terminar de cargarse la vista"""
        self.cargar_estudiantes()

    def cargar_estudiantes(self):
        app = MDApp.get_running_app()
        self.ids.lista_estudiantes.clear_widgets()
        
        # Consultamos la lista relacional de estudiantes
        estudiantes = app.student.consultar_estudiantes()
        for est in estudiantes:
            id_estudiante = est[0]
            cedula = est[1]
            nombre = est[2]
            apellido = est[3]
            
            # Formateamos la fila de la lista
            item = TwoLineAvatarIconListItem(
                text=f"{nombre} {apellido}",
                secondary_text=f"Cédula: {cedula}",
            )
            
            # Botón izquierdo: Editar datos
            btn_editar = IconLeftWidget(icon="pencil", theme_text_color="Custom", text_color=(0, 0.5, 1, 1))
            btn_editar.bind(on_release=lambda x, id_est=id_estudiante, n=nombre, a=apellido, c=cedula: self.preparar_edicion(id_est, n, a, c))
            
            # Botón derecho: Eliminar registro
            btn_eliminar = IconRightWidget(icon="delete", theme_text_color="Custom", text_color=(1, 0, 0, 1))
            btn_eliminar.bind(on_release=lambda x, id_est=id_estudiante: self.eliminar_estudiante(id_est))
            
            # Agregamos los sub-componentes a la fila en el orden correcto
            item.add_widget(btn_editar)
            item.add_widget(btn_eliminar)
            self.ids.lista_estudiantes.add_widget(item)

    def agregar_estudiante(self, nombre, apellido, cedula):
        # Validación básica de campos vacíos
        if not nombre.strip() or not cedula.strip() or not apellido.strip():
            return 
            
        app = MDApp.get_running_app()
        
        if self.id_estudiante_a_editar is not None:
            try:
                #Editar el estudiante seleccionado
                app.student.update_estudiante(self.id_estudiante_a_editar, int(cedula), nombre.strip(), apellido.strip())
                print("¡Estudiante actualizado con éxito!")
                self.id_estudiante_a_editar = None 
            except Exception as e:
                print(f"Error al actualizar: {e}")
        else:
            #Crear Estudiante normal 
            id_new_student = app.persona.registrar_persona(int(cedula), nombre.strip(), apellido.strip())
            app.student.registrar_estudiante(id_new_student)
            print("¡Estudiante registrado con éxito!")

        self.ids.input_nombre.text = ""
        self.ids.input_apellido.text = ""
        self.ids.input_cedula.text = ""
        
        # Regresamos el texto original del botón
        self.ids.id_boton_registrar_estudiante.text = "Registrar Estudiante"
        
        # refrezco de la interfaz
        self.cargar_estudiantes()

    def eliminar_estudiante(self, id_estudiante):
        app = MDApp.get_running_app()
        app.student.delete_estudiante(id_estudiante)
        self.cargar_estudiantes()

    def preparar_edicion(self, id_estudiante, nombre, apellido, cedula):
        # Capturamos el identificador único
        self.id_estudiante_a_editar = id_estudiante
        # Transferimos los datos hacia los inputs
        self.ids.input_nombre.text = nombre
        self.ids.input_apellido.text = apellido
        self.ids.input_cedula.text = str(cedula)
        # Cambiamos El texto de el boton para mas dinamismo
        self.ids.id_boton_registrar_estudiante.text = "Guardar Cambios"