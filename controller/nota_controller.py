from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp

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

    def cargar_calificaciones(self):
        pass