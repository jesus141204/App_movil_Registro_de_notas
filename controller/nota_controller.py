from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.list import ThreeLineAvatarIconListItem, IconRightWidget, IconLeftWidget
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField

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
            
            # Creamos una "llave única" combinando (ID Alumno, ID Materia)
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

        # Se construye la tarjeta de kivy
        for expediente, info in archivador.items():
            notas_reales = info["lista_de_notas"]
            
            # Convertimos los números a texto y rellenamos con "-" hasta tener 5 espacios
            bloque_texto = [str(n) for n in notas_reales]
            while len(bloque_texto) < 5:
                bloque_texto.append("-")
            
            # Unimos las notas con barras: "15 | 18 | - | - | -"
            notas_separadas = " | ".join(bloque_texto)
            
            # Calculamos el promedio matemático real
            promedio = sum(notas_reales) / len(notas_reales) if notas_reales else 0
            
            # Creamos la tarjeta nativa de KivyMD de 3 líneas
            tarjeta = ThreeLineAvatarIconListItem(
                text=info["alumno"],
                secondary_text=f"Materia: {info['materia']}",
                tertiary_text=f"[{notas_separadas}]   •   Promedio: {promedio:.1f}",
                on_release=lambda x, id_a=info["id_a"], id_m=info["id_m"]: self.ir_a_editar_notas(id_a, id_m)
            )
            
            tarjeta.add_widget(IconLeftWidget(icon="school"))
            
            # Le pegamos el bote de basura a la derecha y le configuramos el truco del botón
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
            pantalla_editar = self.manager.get_screen("pantalla_detalle_nota")
            
            # Le ordenamos que cargue los TextFields dinámicos antes de mostrarse
            pantalla_editar.cargar_datos_editar(id_estudiante, codigo_materia)
            
            # Hacemos la transición fluida hacia la izquierda
            self.manager.transition.direction = "left"
            self.manager.current = "pantalla_detalle_nota"
            
# FORMULARIO PARA AGREGAR
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
            
        # 1. Limpiamos lo que haya en pantalla de consultas previas
        self.ids.contenedor_inputs.clear_widgets()
        self.campos_dinamicos.clear()
        
        # 2. Consultamos cuántas notas reales ya existen en SQLite
        notas_existentes = self.app.nota.contar_notas_estudiante(self.id_estudiante_sel, self.codigo_materia_sel)
        self.slots_disponibles = 5 - notas_existentes
        
        if self.slots_disponibles <= 0:
            print("¡Error! Este alumno ya tiene las 5 notas reglamentarias en la Base de Datos.")
            self.ocultar_boton_mas()
            return
            
        # 3. Agregamos automáticamente la primera fila para empezar a escribir
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
        
        # 🔄 CONTROL DEL BOTÓN DE "+": 
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

class DetalleNotaScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        #  Lista clave: Guardará los IDs de SQLite emparejados con sus inputs de la interfaz
        self.mapeo_inputs = [] 

    def cargar_datos_editar(self, id_estudiante, codigo_materia):
        """Se ejecuta antes de entrar a la pantalla para rellenar los datos actuales"""
        # Limpiamos rastros de ediciones anteriores
        self.ids.contenedor_edicion.clear_widgets()
        self.mapeo_inputs.clear()

        # Consultamos las calificaciones reales de este alumno
        notas_bd = self.app.nota.consultar_notas_especificas(id_estudiante, codigo_materia)
        if not notas_bd:
            return

        # Rellenamos las etiquetas superiores con la info de la primera fila
        _, nombre_alumno, nombre_materia, _, _ = notas_bd[0]
        self.ids.lbl_alumno.text = f"Estudiante: {nombre_alumno}"
        self.ids.lbl_materia.text = f"Materia: {nombre_materia}"

        # Recorremos cada evaluación para crearle su fila de edición
        for indice, fila in enumerate(notas_bd):
            id_nota, _, _, valor_nota, fecha_eval = fila

            fila_layout = MDBoxLayout(orientation='horizontal', spacing="12dp", adaptive_height=True)
            
            # Input de nota con el valor actual precargado
            txt_nota = MDTextField(text=str(valor_nota), hint_text=f"Nota #{indice + 1}", input_filter="float", size_hint_x=0.4)
            # Input de fecha con el valor actual precargado
            txt_fecha = MDTextField(text=str(fecha_eval), hint_text="Fecha (AAAA-MM-DD)", size_hint_x=0.6)

            fila_layout.add_widget(txt_nota)
            fila_layout.add_widget(txt_fecha)
            
            # Inyectamos visualmente en el contenedor del archivo .kv
            self.ids.contenedor_edicion.add_widget(fila_layout)

            # Guardamos la relación en memoria para saber qué ID actualizar luego
            self.mapeo_inputs.append({
                "id_nota": id_nota,
                "input_nota": txt_nota,
                "input_fecha": txt_fecha
            })

    def actualizar_calificaciones(self):
        """Recorre las cajas de texto y procesa los cambios en la BD"""
        for item in self.mapeo_inputs:
            id_n = item["id_nota"]
            nota_modificada = item["input_nota"].text
            fecha_modificada = item["input_fecha"].text

            if not nota_modificada or not fecha_modificada:
                print("¡Error! No puedes guardar campos vacíos.")
                return

            # Ejecutamos el update en SQLite para cada fila individual modificada
            self.app.nota.update_notas(id_n, float(nota_modificada), fecha_modificada)

        print("¡Todas las modificaciones guardadas exitosamente!")
        
        # 🔄 Refrescamos la lista de la pantalla principal para que se vean los cambios de inmediato
        self.manager.get_screen("pantalla_notas").cargar_calificaciones()
        self.regresar()

    def regresar(self):
        self.manager.transition.direction = "right"
        self.manager.current = "pantalla_notas"