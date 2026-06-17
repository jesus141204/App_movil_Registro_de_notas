import sqlite3
import bcrypt
import re
from contextlib import closing
class ConnectionModel():
    def __init__(self):
        self.__db_name='db_nota.sqlite3'
        self.__schema_sql='models/schema.sql'
    def __obtener_conexion(self):
            #emitiendo conexion de la db 
            conect=sqlite3.connect(self.__db_name)
            #Activando las claves foraneas para esta sesion
            conect.execute("PRAGMA foreign_keys=ON;")
            return closing(conect) # se decuelve para uso del with
    
    def create_tables_auto(self):
        try:
            with open(self.__schema_sql,"r",encoding='utf-8')as archivo_sql:
                esquema=archivo_sql.read()
                
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.__schema_sql}")
            return             
                                         
        with self.__obtener_conexion() as conect:
                with conect:
                    cursor=conect.cursor()
                    #ejecutando el archivo de script
                    cursor.executescript(esquema)
        print("tablas creada satisfactoriamente")
    
    def ejecutar_consulta(self, query: str, parametros: tuple = ()):
        with self.__obtener_conexion() as conect:
            with conect:
                cursor = conect.cursor()
                cursor.execute(query, parametros)
                
                #Si la consulta empieza con SELECT, es para consultar los datos
                if query.strip().upper().startswith("SELECT"):
                    return cursor.fetchall()
                
                # Si es INSERT, quiero el retorno de la id
                elif query.strip().upper().startswith("INSERT"):
                    return cursor.lastrowid
                
                # Si es UPDATE o DELETE, solo quiero saber las filas
                else:
                    return cursor.rowcount
                              
class PersonaModel():
    def __init__(self,conexion):
            self.__db=conexion
    
    def consultar_personas(self):
        query_persona="SELECT * FROM persona;"
        all_persona=self.__db.ejecutar_consulta(query_persona)
        for persona in all_persona:
            print(persona)
        return all_persona
    
    def registrar_persona(self,cedula,nombre,apellido):
        input_persona=(cedula,nombre,apellido)
        insert_query=''' INSERT INTO persona(cedula,nombre,apellido) values(?,?,?);'''
        id=self.__db.ejecutar_consulta(insert_query,input_persona)
        print("persona registrada")
        return id
                
    def delete_persona(self,id):
        delete_query=(''' DELETE FROM persona where id = ?;  ''')
        self.__db.ejecutar_consulta(delete_query,(id,))
        print("persona eliminada satisfactoriamente")
    
    def update_persona(self,id:int,cedula:int,nombre:str,apellido:str):
        updates_dates=(cedula,nombre,apellido,id)
        query_update=(''' UPDATE persona SET cedula=? , nombre=?, apellido=? where id= ?; ''')
        self.__db.ejecutar_consulta(query_update,updates_dates)
        print(" el usuario fue actualizado")
        
class UserModel():
    @staticmethod
    def hash_password(password):
        password=password
        #convertir a bytes
        bytes_passw=password.encode('utf-8')
        # generarndo salt y hasheando la contraseña 
        salt = bcrypt.gensalt()
        hashed=bcrypt.hashpw(bytes_passw,salt)
        return hashed
    
    @staticmethod
    def validar_estructura_password(password) -> bool:
        """
        Valida que la contraseña tenga entre 8 y 16 caracteres
        y al menos un carácter especial.
        """
        patron = r'^(?=.*[!@#$%^&*(),.?":{}|<>]).{8,16}$'
        # re.match devuelve un objeto si coincide, o None si no. Lo convertimos a booleano.
        return bool(re.match(patron, password))

    def __init__(self,conexion):
        self.__db=conexion
        
    def get_users(self) :   
        query_select_username=''' SELECT * FROM user '''
        print("usernames consultado satisfactoriamente")
        result=self.__db.ejecutar_consulta(query_select_username)
        return result

    def get_only_user(self,user) :   
        query_select_username=''' SELECT id,username,is_admin FROM user where username = ? '''
        print("username consultado satisfactoriamente")
        result=self.__db.ejecutar_consulta(query_select_username,(user,))
        return result
                
    def get_password_by_username(self,username):
        query_get_by_password=''' SELECT password FROM user where username=? '''
        result=self.__db.ejecutar_consulta(query_get_by_password,(username,))
        return result
    
    def verificar_credenciales(self,username,password)->bool: 
        #se buscara la contraseña para ese dicho usuario      
        password_guardada=None  
        result=self.get_password_by_username(username)
        
        if not result:#Si el resultado esta vacio retorna falso
            return False
        
        if not self.validar_estructura_password(password):
            print("Error: La contraseña no cumple con los requisitos de seguridad.")
            return False # Retornamos False para usarlo en el controlador
        
        for passw in result:#obteniendo la clave
            password_guardada=passw[0]
        # conviertiendo en bytes para comparar las claves
        bytes_input=password.encode('utf-8')
        bytes_guardada= password_guardada.encode('utf-8')
        
        return True if bcrypt.checkpw(bytes_input,bytes_guardada) else False
        
    
    def register_user(self,username,password,id_persona,is_admin):
        if not self.validar_estructura_password(password):
            print("Error: La contraseña no cumple con los requisitos de seguridad.")
            return False # Retornamos False para usarlo en el controlador
        
        #Validamos la contraseña antes de registrar o hashear
        hash_password=self.hash_password(password).decode('utf-8')
        input_user=(username,hash_password,id_persona,is_admin)
        insert_query=''' INSERT INTO user(username,password,id_persona,is_admin) values(?,?,?,?);'''
        result=self.__db.ejecutar_consulta(insert_query,input_user)
        print("usuario ingresado satisfactoriamente")
        return result
    
    def delete_user(self,id_user):
        delete_query=(''' DELETE FROM user where id = ?;  ''')
        result=self.__db.ejecutar_consulta(delete_query,(id_user,))
        print("usuario eliminado satisfactoriamente")
        return result

class MateriaModel():
    def __init__(self, conexion):
        self.__db = conexion
    
    def consultar_materias(self):
        query_materia = "SELECT * FROM materia;"
        all_materia = self.__db.ejecutar_consulta(query_materia)
        return all_materia
        
    def registrar_materia(self, materia):
        query_insert = " INSERT INTO materia(name) VALUES (?) "
        id_materia = self.__db.ejecutar_consulta(query_insert, (materia,))
        print("Materia registrada")
        return id_materia
    
    def update_materia(self, id, name):
        updates_materia = (name, id)
        update_query = " UPDATE materia SET name=? where codigo_materia=? "
        self.__db.ejecutar_consulta(update_query, updates_materia)
        
    def delete_materia(self, id):
        delete_query = ''' DELETE FROM materia where codigo_materia = ?; '''
        self.__db.ejecutar_consulta(delete_query, (id,))
        print("Materia eliminada satisfactoriamente")

class studentModel():
    def __init__(self, conexion):
        self.__db = conexion
    
    def consultar_estudiantes(self):
        query_materia = """SELECT estudiante.id, persona.cedula, persona.nombre, persona.apellido 
                    FROM estudiante 
                    INNER JOIN persona ON estudiante.id_persona = persona.id;"""
        all_students = self.__db.ejecutar_consulta(query_materia)
        return all_students
        
    def registrar_estudiante(self, id_persona):
        query_insert = " INSERT INTO estudiante(id_persona) VALUES (?) "
        id_estudiante = self.__db.ejecutar_consulta(query_insert, (id_persona,))
        return id_estudiante
    
    def update_estudiante(self, id_estudiante: int, cedula: int, nombre: str, apellido: str):
        query_update = ''' 
            UPDATE persona 
            SET cedula = ?, nombre = ?, apellido = ? 
            WHERE id = (SELECT id_persona FROM estudiante WHERE id = ?);
        '''
        parametros = (cedula, nombre, apellido, id_estudiante)
        self.__db.ejecutar_consulta(query_update, parametros)
        print("El estudiante heredado de persona fue actualizado correctamente")
        
    def delete_estudiante(self, id):
        delete_query = ''' DELETE FROM estudiante where id = ?; '''
        self.__db.ejecutar_consulta(delete_query, (id,))
        print("Estudiante eliminado satisfactoriamente")

class notaModel():
    def __init__(self,conexion):
        self.__db=conexion
    
    def consultar_notas(self):
        query_notas="SELECT * FROM notas;"
        all_notas=self.__db.ejecutar_consulta(query_notas)
        return all_notas
        
    def registrar_notas(self,id_estudiante,id_usuario,nota,fecha_evaluacion,codigo_materia):
        input_nota=(id_estudiante,id_usuario,nota,fecha_evaluacion,codigo_materia)
        query_insert=" INSERT INTO notas(id_estudiante,id_usuario,nota,fecha_evaluacion,codigo_materia) VALUES (?,?,?,?,?)   "
        id_notas=self.__db.ejecutar_consulta(query_insert,input_nota)
        return id_notas
        
    def update_notas(self,id,name,fecha):
        updates_materia=(name,fecha,id)
        update_query="  UPDATE notas SET nota=?,fecha_evaluacion=? where id=? "
        self.__db.ejecutar_consulta(update_query,updates_materia)
        
    def delete_notas(self,id):
        delete_query=(''' DELETE FROM notas where id = ?;  ''')
        self.__db.ejecutar_consulta(delete_query,(id,))
        print("notas eliminada satisfactoriamente")
    
    def contar_notas_estudiante(self, id_estudiante, codigo_materia):
        query = """
            SELECT COUNT(*) FROM notas 
            WHERE id_estudiante = ? AND codigo_materia = ?
        """
        resultado = self.__db.ejecutar_consulta(query, (id_estudiante, codigo_materia))
        
        if resultado:
            primera_fila = resultado[0]
            total_notas = primera_fila[0]
            return total_notas
    
        return 0

    def consultar_notas_con_nombres(self):
        """Trae las calificaciones asociando los nombres reales de estudiantes y materias"""
        # NOTA: Ajusta los nombres de las tablas/columnas ('estudiantes', 'materias', 'nombre') 
        query = """
            SELECT p.nombre, m.name, n.nota, n.id_estudiante, n.codigo_materia 
            FROM notas n
            JOIN estudiante e ON n.id_estudiante = e.id
            JOIN materia m ON n.codigo_materia = m.codigo_materia
            JOIN persona p ON e.id_persona = p.id
        """
        return self.__db.ejecutar_consulta(query)

    def delete_bloque_notas(self, id_estudiante, codigo_materia):
        """Elimina todas las notas que pertenecen a un estudiante en una materia específica"""
        delete_query = """
            DELETE FROM notas 
            WHERE id_estudiante = ? AND codigo_materia = ?;
        """
        self.__db.ejecutar_consulta(delete_query, (id_estudiante, codigo_materia))
        print(f"Bloque de notas eliminado satisfactoriamente para Alumno: {id_estudiante}")
    
    def consultar_notas_especificas(self, id_estudiante, codigo_materia):
        """Trae las notas detalladas de un solo estudiante en una sola materia"""
        query = """
            SELECT n.id, p.nombre, m.name, n.nota, n.fecha_evaluacion
            FROM notas n
            JOIN estudiante e ON n.id_estudiante = e.id
            JOIN materia m ON n.codigo_materia = m.codigo_materia
            JOIN persona p ON e.id_persona = p.id
            WHERE n.id_estudiante = ? AND n.codigo_materia = ?
        """
        return self.__db.ejecutar_consulta(query, (id_estudiante, codigo_materia))
        
"""
con=ConnectionModel()
user=UserModel(con)
p=PersonaModel(con)
p.registrar_persona(3145642,"Jesus","Marin")
user.register_user("ale14","141204.j",1,True)
"""