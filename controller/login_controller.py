from kivymd.uix.screen import MDScreen
from kivymd.app import MDApp
class LoginScreen(MDScreen):
    def __init__(self,*args, **kwargs):
        super().__init__(*args, **kwargs)
        self.app=MDApp.get_running_app()
        
    def on_pre_enter(self, *args):
        #Limpiamos las entradas
        self.ids.txt_usuario.text = ""
        self.ids.txt_password.text = ""
        # 1. Limpiamos el mensaje de error o éxito por completo
        self.ids.lbl_error.text = ""

    def verificar_credenciales(self, usuario, password):
        """Este método es llamado directamente desde el archivo .kv"""
        # 1. Limpiamos cualquier mensaje de error previo
        self.ids.lbl_error.text = ""
        # 2. Validaciones básicas de campos vacíos
        cls_usuario=usuario.strip()
        cls_password=password.strip()
        if not cls_usuario or not cls_password:
            self.ids.lbl_error.theme_text_color="Error"
            self.ids.lbl_error.text = "Por favor, llena todos los campos."
            return

        if self.app.user.verificar_credenciales(cls_usuario,cls_password):
            print("Login Funciona yupi")
            self.ids.lbl_error.theme_text_color="Custom"
            self.ids.lbl_error.text_color = (0, 0.6, 0, 1) 
            self.ids.lbl_error.text = "¡Acceso concedido!"
            #Obteniendo los datos del usuario al confirmar su entrada
            log_in_user = self.app.user.get_only_user(cls_usuario) 
            if log_in_user:
                id_user,username,admin,id_persona =log_in_user[0]
                self.app.sesion_usuario={
                    "id_usuario":id_user,
                    "username":username,
                    "is_admin":admin,
                    "id_persona":id_persona
                }
                print(f"Sesion iniciada Identificador:{self.app.sesion_usuario['id_usuario']} con username {self.app.sesion_usuario['username']}")
            #transicion a la pantalla notas
            self.manager.transition.direction = "left"
            self.manager.current = "pantalla_notas"
            
        else:
            # Si falla, modificamos el Label de error usando su ID
            self.ids.lbl_error.text = "Usuario o contraseña incorrectos."