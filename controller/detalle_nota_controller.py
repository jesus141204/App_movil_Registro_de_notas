from kivy.uix.screenmanager import Screen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDIconButton 
from kivymd.app import MDApp

class DetalleNotaScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        self.mapeo_inputs = [] 
        self.id_estudiante_sel = None
        self.codigo_materia_sel = None

    def cargar_datos_editar(self, id_estudiante, codigo_materia):
        """Prepara los datos existentes y habilita slots libres hasta el límite de 5"""
        self.ids.contenedor_edicion.clear_widgets()
        self.mapeo_inputs.clear()
        
        self.id_estudiante_sel = id_estudiante
        self.codigo_materia_sel = codigo_materia

        # Consultamos las notas actuales en la BD
        notas_bd = self.app.nota.consultar_notas_especificas(id_estudiante, codigo_materia)
        
        if notas_bd:
            _, nombre_alumno, nombre_materia, _, _ = notas_bd[0]
            self.ids.lbl_alumno.text = f"Estudiante: {nombre_alumno}"
            self.ids.lbl_materia.text = f"Materia: {nombre_materia}"

        cant_existentes = len(notas_bd) if notas_bd else 0

        # mostrando las notas para editar o eliminar
        if notas_bd:
            for indice, fila in enumerate(notas_bd):
                id_nota, _, _, valor_nota, fecha_eval = fila

                fila_layout = MDBoxLayout(orientation='horizontal', spacing="12dp", adaptive_height=True)
                
                txt_nota = MDTextField(text=str(valor_nota), hint_text=f"Nota #{indice + 1}", input_filter="float", size_hint_x=0.3)
                txt_fecha = MDTextField(text=str(fecha_eval), hint_text="Fecha (AAAA-MM-DD)", size_hint_x=0.5)
                
                # Botón para eliminar esta nota específica
                btn_eliminar = MDIconButton(
                    icon="trash-can-outline",
                    theme_icon_color="Custom",
                    icon_color=(0.9, 0.2, 0.2, 1), # Color rojo para alertar peligro
                    size_hint_x=0.2
                )
                # Vinculamos el botón usando una clausura para congelar el id_nota de esta fila
                btn_eliminar.bind(on_release=lambda x, id_n=id_nota: self.borrar_nota_individual(id_n))

                fila_layout.add_widget(txt_nota)
                fila_layout.add_widget(txt_fecha)
                fila_layout.add_widget(btn_eliminar) # Inyectamos el botón en la fila
                
                self.ids.contenedor_edicion.add_widget(fila_layout)

                self.mapeo_inputs.append({
                    "id_nota": id_nota,
                    "input_nota": txt_nota,
                    "input_fecha": txt_fecha
                })

        # para mostrar los espacios vacion de las otas restantes
        # Nota: Estas no llevan botón de borrar porque aún no existen en la Base de Datos
        slots_restantes = 5 - cant_existentes
        for i in range(slots_restantes):
            num_nota = cant_existentes + i + 1
            fila_layout = MDBoxLayout(orientation='horizontal', spacing="12dp", adaptive_height=True)
            
            txt_nota = MDTextField(hint_text=f"Nota #{num_nota} (Nueva)", input_filter="float", size_hint_x=0.4)
            txt_fecha = MDTextField(hint_text="Fecha (AAAA-MM-DD)", size_hint_x=0.6)

            fila_layout.add_widget(txt_nota)
            fila_layout.add_widget(txt_fecha)
            
            self.ids.contenedor_edicion.add_widget(fila_layout)

            self.mapeo_inputs.append({
                "id_nota": None,
                "input_nota": txt_nota,
                "input_fecha": txt_fecha
            })

    def borrar_nota_individual(self, id_nota):
        """Elimina la nota de la BD y refresca la pantalla actual de inmediato"""
        print(f"Eliminando nota individual con ID: {id_nota}")
        
        # Eliminamos la nota indv
        self.app.nota.eliminar_nota_individual(id_nota)
        
        # Al volver a llamarse, detectará un registro menos en la BD y creará un slot vacío nuevo.
        self.cargar_datos_editar(self.id_estudiante_sel, self.codigo_materia_sel)

    def actualizar_calificaciones(self):
        """Procesa de manera híbrida: UPDATE para lo viejo, INSERT para lo nuevo"""
        id_profesor = self.app.sesion_usuario["id_usuario"]
        
        for item in self.mapeo_inputs:
            id_n = item["id_nota"]
            nota_modificada = item["input_nota"].text
            fecha_modificada = item["input_fecha"].text

            if not nota_modificada or not fecha_modificada:
                if id_n is not None:
                    print("¡Error! No puedes dejar vacíos campos de notas que ya existían.")
                    return
                else:
                    continue

            if id_n is not None:
                self.app.nota.update_notas(id_n, float(nota_modificada), fecha_modificada)
            else:
                self.app.nota.registrar_notas(
                    id_estudiante=self.id_estudiante_sel,
                    id_usuario=int(id_profesor),
                    nota=float(nota_modificada),
                    fecha_evaluacion=fecha_modificada,
                    codigo_materia=self.codigo_materia_sel
                )

        print("¡Base de Datos Sincronizada Exitosamente!")
        self.manager.get_screen("pantalla_notas").cargar_calificaciones()
        self.regresar()

    def regresar(self):
        self.manager.transition.direction = "right"
        self.manager.current = "pantalla_notas"