from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager
from kivy.core.window import Window
# Importación de controladores
from controller.login_controller import LoginScreen
from controller.nota_controller import NotasScreen
<<<<<<< Updated upstream
from controller.detalle_nota_controller import DetalleNotaScreen
from controller.registrar_nota_controller import RegistrarNotaScreen 
=======
#from controller.detalle_nota_controller import DetalleNotaScreen
from controller.update_notas_controller import UpdateNotasScreen
from controller.registrar_nota_controller import RegistrarNotaScreen 
from controller.detalle_nota_controller import DetalleNotaScreen 
>>>>>>> Stashed changes
# Nota: Como StudentView es un MDBoxLayout, asegúrate de cómo lo integras en tus pantallas
from controller.student_controller import StudentView 
from controller.materia_controller import MateriaView
# Importación de modelos
from models.model import PersonaModel, UserModel, ConnectionModel, studentModel, notaModel, MateriaModel

Window.size=(350,600)

# Instanciando afuera la conexión
conexion = ConnectionModel()

class LoginApp(MDApp):
    def build(self):
        #Variable global sobre el usuario
        self.sesion_usuario=None
        # Instanciando el global de los modelos para acceso desde cualquier vista
        self.persona = PersonaModel(conexion)
        self.user = UserModel(conexion)
        self.materia = MateriaModel(conexion)
        self.student = studentModel(conexion)
        self.nota = notaModel(conexion)
        # Otras configuraciones de diseño
        self.title = "Sistema de registro de notas"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Red"
        
        # Cargamos los archivos de diseño de la carpeta views
        Builder.load_file('views/login_view.kv')
        Builder.load_file('views/materia_view.kv')
        Builder.load_file('views/student_view.kv')
        Builder.load_file('views/nota_view.kv')
        Builder.load_file('views/update_notas_view.kv') 
        Builder.load_file('views/registrar_nota_view.kv')
        Builder.load_file('views/detalle_nota_view.kv')
        # Gestor de pantallas
        sm = ScreenManager()
        # Agregamos las pantallas principales
        sm.add_widget(LoginScreen(name="pantalla_login"))
        sm.add_widget(NotasScreen(name="pantalla_notas"))
<<<<<<< Updated upstream
        
        #  Agregamos las dos pantallas del nuevo flujo
        sm.add_widget(RegistrarNotaScreen(name="pantalla_registrar_nota"))
        sm.add_widget(DetalleNotaScreen(name="pantalla_detalle_nota"))
        
=======
        #  Agregamos las pantallas del flujo de notas
        sm.add_widget(RegistrarNotaScreen(name="pantalla_registrar_nota"))
        sm.add_widget(UpdateNotasScreen(name="pantalla_update_notas"))
        sm.add_widget(DetalleNotaScreen(name="pantalla_detalle_notas"))
>>>>>>> Stashed changes
        return sm
    
if __name__ == '__main__':
    conexion.create_tables_auto()
    LoginApp().run()