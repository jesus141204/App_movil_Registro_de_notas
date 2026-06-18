from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
<<<<<<< Updated upstream
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget, IconLeftWidget

=======
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget,IconLeftWidget
>>>>>>> Stashed changes
class NotasScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        
    def logout(self):
        #Destruimos la sesion 
        self.app.sesion_usuario=None
        print("Sesion Destruida")
        #Redirigimos a Login
        self.manager.transition.direction = "right"
        self.manager.current = "pantalla_login"
        
    def on_enter(self, *args):
        """Se ejecuta automáticamente cada vez que esta pantalla se vuelve visible"""
        print("¡Bienvenido al Panel Principal de Notas!")
        self.cargar_calificaciones()
    
    def ir_a_registrar(self):
        """Manda a la vista de formulario"""
        self.manager.transition.direction = "left"
        self.manager.current = "pantalla_registrar_nota"

    def cargar_calificaciones(self):
        # Limpiando los widgets o elementos de la vista
        self.ids.lista_notas.clear_widgets()
        
        # Traer todas las filas sueltas de la Base de Datos
        notas_sueltas = self.app.nota.consultar_notas_con_nombres()
        if not notas_sueltas:
            print("No hay nada en la Base de Datos.")
            return

        # Oorganizar (Agrupar las notas por alumno y materia)
        archivador = {}
        
        for fila in notas_sueltas:
            nombre_alumno, nombre_materia, valor_nota, id_alumno, id_materia = fila
            
<<<<<<< Updated upstream
            # Creamos una "llave única" combinando (ID Alumno, ID Materia)
=======
            # Creamos una llave única combinando (ID Alumno, ID Materia)
>>>>>>> Stashed changes
            expediente = (id_alumno, id_materia)
            
            # Si es la primera vez que vemos a este alumno en esta materia, le creamos su carpeta
            if expediente not in archivador:
                archivador[expediente] = {
                    "alumno": nombre_alumno,
                    "materia": nombre_materia,
                    "lista_de_notas": [],
                    "id_a": id_alumno,
                    "id_m": id_materia
                }
            
            # Metemos la nota actual dentro de su carpeta correspondientemente
            archivador[expediente]["lista_de_notas"].append(valor_nota)

<<<<<<< Updated upstream
        # Se construye la tarjeta de kivy
        for expediente, info in archivador.items():
            notas_reales = info["lista_de_notas"]
            
            # Convertimos los números a texto y rellenamos con "-" hasta tener 5 espacios
            bloque_texto = [str(n) for n in notas_reales]
            while len(bloque_texto) < 5:
                bloque_texto.append("-")
            
            # Unimos las notas con barras: "15 | 18 | - | - | -"
            notas_separadas = " | ".join(bloque_texto)
=======
           # Se construye la tarjeta de kivy
        for expediente, info in archivador.items():
            notas_reales = info["lista_de_notas"]
            
            # Quitamos el .0 si es entero y las unimos con comas limpias
            # Notas: 16, 12
            notas_limpias = [str(int(n) if n.is_integer() else n) for n in notas_reales]
            texto_notas = ", ".join(notas_limpias)
>>>>>>> Stashed changes
            
            # Calculamos el promedio matemático real
            promedio = sum(notas_reales) / len(notas_reales) if notas_reales else 0
            
            # Creamos la tarjeta nativa de KivyMD de 3 líneas
            tarjeta = ThreeLineAvatarIconListItem(
                text=info["alumno"],
                secondary_text=f"Materia: {info['materia']}",
<<<<<<< Updated upstream
                tertiary_text=f"[{notas_separadas}]   •   Promedio: {promedio:.1f}",
                on_release=lambda x, id_a=info["id_a"], id_m=info["id_m"]: self.ir_a_editar_notas(id_a, id_m)
            )
            
            tarjeta.add_widget(IconLeftWidget(icon="school"))
            
            # Le pegamos el bote de basura a la derecha y le configuramos el truco del botón
=======
                tertiary_text=f"Notas:({texto_notas}) • DEF:{promedio:.1f} pts", 
                on_release=lambda x, id_a=info["id_a"], id_m=info["id_m"]: self.ir_a_detalle_notas(id_a, id_m) 
            )
            
            # Boton izquierdo  Editar Notas
            btn_editar = IconLeftWidget(icon="pencil", theme_text_color="Custom", text_color=(0, 0.5, 1, 1))
            btn_editar.bind(on_release=lambda x, id_a=info["id_a"], id_m=info["id_m"]: self.ir_a_editar_notas(id_a, id_m))
            tarjeta.add_widget(btn_editar)
            
            #Boton derecho de eliminar todas las notas
>>>>>>> Stashed changes
            btn_borrar = IconRightWidget(icon="delete")
            btn_borrar.bind(on_release=lambda x, id_e=info["id_a"], cod_m=info["id_m"]: self.eliminar_bloque_completo(id_e, cod_m))
            tarjeta.add_widget(btn_borrar)
            
            # Metemos la tarjeta terminada al diseño de la vista (.kv)
            self.ids.lista_notas.add_widget(tarjeta)

    def eliminar_bloque_completo(self, id_estudiante, codigo_materia):
        """Borra todo de una vez y refresca la pantalla"""
        print(f"Borrando registros del alumno {id_estudiante}")
        self.app.nota.delete_bloque_notas(id_estudiante, codigo_materia)
        self.cargar_calificaciones() # Volvemos a llamar a la función de arriba para actualizar la pantalla

    def ir_a_editar_notas(self, id_estudiante, codigo_materia):
            """Prepara los datos en la pantalla de detalles y cambia de vista"""
            print(f"Abriendo edición para Alumno ID: {id_estudiante}, Materia Código: {codigo_materia}")
            
            # Buscamos la pantalla de destino mediante el ScreenManager
<<<<<<< Updated upstream
            pantalla_editar = self.manager.get_screen("pantalla_detalle_nota")
=======
            pantalla_editar = self.manager.get_screen("pantalla_update_notas")
>>>>>>> Stashed changes
            
            # Le ordenamos que cargue los TextFields dinámicos antes de mostrarse
            pantalla_editar.cargar_datos_editar(id_estudiante, codigo_materia)
            
            # Hacemos la transición fluida hacia la izquierda
            self.manager.transition.direction = "left"
<<<<<<< Updated upstream
            self.manager.current = "pantalla_detalle_nota"
            
=======
            self.manager.current = "pantalla_update_notas"  
    
    #Ir a detalles de la notas de un estudiante
    def ir_a_detalle_notas(self, id_estudiante, codigo_materia):
        """Prepara los datos de solo lectura en la pantalla de detalles y cambia de vista"""
        print(f"Abriendo vista de detalles para Alumno ID: {id_estudiante}, Materia Código: {codigo_materia}")
        
        # Buscamos la pantalla de detalles por su nombre asignado en el ScreenManager
        pantalla_detalle = self.manager.get_screen("pantalla_detalle_notas")
        
        # Invocamos su función pasándole los IDs correspondientes
        pantalla_detalle.show_allnotes_student(id_estudiante, codigo_materia)
        
        # Transición de cambio de pantalla fluida
        self.manager.transition.direction = "left"
        self.manager.current = "pantalla_detalle_notas"
>>>>>>> Stashed changes
