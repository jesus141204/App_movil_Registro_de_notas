from kivy.uix.screenmanager import Screen
from kivymd.uix.list import OneLineListItem
from kivymd.app import MDApp

class DetalleNotaScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.app = MDApp.get_running_app()
        
    def show_allnotes_student(self, id_estudiante, codigo_materia):
        """Carga la información de la BD y la muestra de forma limpia en la pantalla"""
        
        # Limpiamos la lista visual para borrar el alumno anterior que hayamos consultado
        self.ids.contenedor_notas_simples.clear_widgets()
        
        #  Buscamos en la Base de Datos las notas de este estudiante específico
        notas_bd = self.app.nota.consultar_notas_especificas(id_estudiante, codigo_materia)
        
        # Control de seguridad: Si la consulta viene vacía, reseteamos los textos y paramos
        if not notas_bd:
            self.ids.lbl_alumno.text = "Estudiante: No registrado"
            self.ids.lbl_materia.text = "Materia: No registrada"
            self.ids.lbl_promedio.text = "Promedio: 0.0 pts"
            return

        # Extraemos los nombres usando los datos de la primera fila 
        primera_fila = notas_bd[0]
        nombre_alumno = primera_fila[1]
        nombre_materia = primera_fila[2]
        
        # Asignamos los textos a los Labels principales en la parte superior de la pantalla
        self.ids.lbl_alumno.text = f"Estudiante: {nombre_alumno}"
        self.ids.lbl_materia.text = f"Materia: {nombre_materia}"
        
        # Extraemos el nombre del profesor que inició sesión en la App global
        id_persona_profesor = self.app.sesion_usuario.get("id_persona")
        #datos del profesor que devuelve la consulta
        datos_profesor=self.app.user.get_datos_persona_ofuser(id_persona_profesor) 
        
        #Recorremos y desempaquetamos directamente las columnas por su nombre
        for cedula, nombre, apellido in datos_profesor:
            self.ids.lbl_docente.text = f"Docente: {nombre} {apellido}"
            break # Forzamos la salida en la primera fila por seguridad
        else:
            self.ids.lbl_docente.text = "Docente: Profesor Autorizado"
        
        # Recorremos unicamente las notas reales que existen en la BD 
        suma_para_promedio = 0
        
        for indice, fila in enumerate(notas_bd):
            valor_nota = fila[3]   # Posición del número de la nota
            fecha_eval = fila[4]   # Posición de la fecha textualmente
            
            # Vamos acumulando la suma de las notas para el paso final
            suma_para_promedio += valor_nota
            
            # Creamos el OneLineListItem Para la informacion de las notas
            linea_sencilla = OneLineListItem(
                text=f"Nota #{indice + 1}:   {valor_nota} pts      |      Fecha: {fecha_eval}"
            )
            # línea limpia dentro de nuestro contenedor del diseño
            self.ids.contenedor_notas_simples.add_widget(linea_sencilla)

        # Calculamos el promedio basándonos en la cantidad exacta de notas que recorrimos
        total_evaluaciones = len(notas_bd)
        promedio = suma_para_promedio / total_evaluaciones if total_evaluaciones > 0 else 0
        
        # Mostramos el promedio final 
        self.ids.lbl_promedio.text = f"Promedio General: {promedio:.1f} pts"
    
    def regresar(self):
        # Transición limpia para volver al panel de control de notas
        self.manager.transition.direction = "right"
        self.manager.current = "pantalla_notas"