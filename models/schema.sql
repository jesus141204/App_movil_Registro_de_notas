CREATE TABLE IF NOT EXISTS  materia(codigo_materia INTEGER PRIMARY KEY AUTOINCREMENT,name text NOT NULL);
            
CREATE TABLE IF NOT EXISTS persona(id INTEGER PRIMARY KEY AUTOINCREMENT,cedula INTEGER UNIQUE CHECK(length(cedula)<=10),
                                    nombre TEXT NOT NULL,apellido TEXT NOT NULL);
                                           
CREATE TABLE IF NOT EXISTS user(id INTEGER PRIMARY KEY AUTOINCREMENT,username  TEXT NOT NULL UNIQUE,password TEXT NOT NULL,id_persona INTEGER UNIQUE,
                                is_admin INTEGER CHECK(is_admin IN(0,1)),
                                FOREIGN KEY (id_persona) REFERENCES persona(id) ON DELETE CASCADE);
            
CREATE TABLE IF NOT EXISTS estudiante(id INTEGER PRIMARY KEY AUTOINCREMENT,id_persona INTEGER UNIQUE,
                                     FOREIGN KEY (id_persona) REFERENCES persona(id) ON DELETE CASCADE );
            
CREATE TABLE IF NOT EXISTS notas(id INTEGER PRIMARY KEY AUTOINCREMENT,id_estudiante INTEGER,id_usuario INTEGER,
                                nota REAL NOT NULL,fecha_evaluacion TEXT NOT NULL,codigo_materia INTEGER ,
                                FOREIGN KEY (id_usuario) REFERENCES user(id) ON DELETE CASCADE,
                                FOREIGN KEY (id_estudiante) REFERENCES estudiante(id) ON DELETE CASCADE,
                                FOREIGN KEY (codigo_materia) REFERENCES materia(codigo_materia) ON DELETE CASCADE);