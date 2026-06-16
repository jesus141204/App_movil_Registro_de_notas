from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
from kivymd.uix.list import OneLineAvatarIconListItem, IconRightWidget, IconLeftWidget

class MateriaView(MDBoxLayout):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Variable para saber que accion se realizara en el metodo agregar_materia
        self.id_materia_a_editar = None
        self.app=MDApp.get_running_app()

    def on_kv_post(self, base_widget):
        """Se ejecuta automáticamente al cargar la pestaña de materias"""
        self.cargar_materias()

    def cargar_materias(self):
        self.ids.lista_materias.clear_widgets()
        
        # Llamamos al modelo de materias que declare global en el main 
        materias = self.app.materia.consultar_materias()
        
        for mat in materias:
            id_materia = mat[0]
            nombre_materia = mat[1]
            
            # Usamos TwoLine para que mantenga el diseño limpio del sistema
            item = OneLineAvatarIconListItem(
                text=f"{nombre_materia}"
                )
            
            # Botón Izquierdo: Editar Materia
            btn_editar = IconLeftWidget(icon="pencil", theme_text_color="Custom", text_color=(0, 0.5, 1, 1))
            btn_editar.bind(on_release=lambda x, id_mat=id_materia, name=nombre_materia: 
                             self.preparar_edicion(id_mat, name))
            
            # Botón Derecho: Eliminar Materia
            btn_eliminar = IconRightWidget(icon="delete", theme_text_color="Custom", text_color=(1, 0, 0, 1))
            btn_eliminar.bind(on_release=lambda x, id_mat=id_materia: self.eliminar_materia(id_mat))
            
            # Lo añadimos al ítem de la lista
            item.add_widget(btn_editar)
            item.add_widget(btn_eliminar)
            self.ids.lista_materias.add_widget(item)

    def agregar_materia(self, nombre_materia):
        # Validación básica de campo vacío
        if not nombre_materia.strip():
            return 
          
        if self.id_materia_a_editar is not None:
            # eleccion de actualizacion
            try:
                self.app.materia.update_materia(self.id_materia_a_editar,nombre_materia.strip())
                print("¡Materia actualizada con éxito!")
                self.id_materia_a_editar = None
            except Exception as e:
                print(f"Error al actualizar materia: {e}")
        else:
            # Eleccion de nueva materia
            self.app.materia.registrar_materia(nombre_materia.strip())
            print("¡Materia registrada con éxito!")

        self.ids.input_nombre_materia.text = ""
        self.ids.id_boton_registrar_materia.text = "Registrar Materia"        
        # Recargamos la lista
        self.cargar_materias()

    def eliminar_materia(self, id_materia):
        self.app.materia.delete_materia(id_materia)
        self.cargar_materias()
        
    def preparar_edicion(self, id_materia, nombre_materia):
        self.id_materia_a_editar = id_materia
        self.ids.input_nombre_materia.text = nombre_materia
        self.ids.id_boton_registrar_materia.text = "Guardar Cambios"