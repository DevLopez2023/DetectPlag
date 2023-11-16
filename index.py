'''
Llamando a las diversas librerias y framework que servirán para la implementación
'''
import cv2  #para uso de opencv, tratamiento de imágenes.
from flask import Flask, abort, render_template, Response, redirect, url_for, session, request
# Para integración de MYSQL en flask
from flask_mysqldb import MySQL
# MySQLdb.cursors --> uso de cursores de MYSQL. (Insert/Update/Select/Delete)
import MySQLdb.cursors
# re --> permiten comprobar si una determinada cadena coincide con una expresión regular dada.
# os --> permite realizar operaciones dependiente del Sistema Operativo como crear una carpeta, listar contenidos de una carpeta, conocer acerca de un proceso, finalizar un proceso, etc. 
import re,os
import numpy as np
# para que los archivos que sean subidos al servidor tengan una extensión segura y apropiada.
from werkzeug.utils import secure_filename

# Libreria imageai para detección de mosquita blanca acorde al modelo personalizado que fue entrenado.
from imageai.Detection.Custom import CustomObjectDetection
# Libreria para detección en tiempo real
#from imageai.Detection import VideoObjectDetection

'''
CONFIGURACIÓN PARA IMÁGENES
'''
# Para el cálculo del tiempo de envio y recepción de un archivo (imagen / caché)
from datetime import timedelta 
# Es el conjunto de extensiones de archivo permitidas.
ALLOWED_EXTENSIONS = set(['jpg', 'png', 'jpeg', 'gif'])
# verificar si la extensión del archivo es válida
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

#Confirmación del archivo principal - Objeto app que permite la creación de más rutas dentro de la aplicación.
app = Flask(__name__)
PORT = 8000
DEBUG = False

'''
DATOS DE CONEXIÓN A BASE DE DATOS
'''
# clave secreta para protección extra
app.secret_key = '123'
# Datos de conexión de la base de datos
# nombre del servidor / host
app.config['MYSQL_HOST'] = 'localhost'
# nombre del usuario MYSQL XAMMP
app.config['MYSQL_USER'] = 'root'
# contraseña de MYSQL
app.config['MYSQL_PASSWORD'] = ''
# nombre de la base de datos
app.config['MYSQL_DB'] = 'detect_taps'

# Inicializar MYSQL
mysql = MySQL(app)

# devuelve el directorio de trabajo actual de un proceso.
execution_path = os.getcwd() 

'''
CONFIGURACIÓN DE CÁMARA WEB 
''' 

# Acceder a la cámara web del ordenador o dispositivo móvil
camara = cv2.VideoCapture(1) 
# Estableciendo la resolución de la cámara, 3 es alta, 4 es ancha  
camara.set(3, 390)
camara.set (3, 390) 

'''
Una vez que se obtuvo el frame, vale recalcar que se deben obtener de manera consecutiva y persistente.
Para ello se debe crear un generador para stremear datos al cliente.
'''

def frames_gen():
    while True: 
        #camara detectada
        ok, imagen = camara.read()
        # si no esta activa
        if not ok:
            # retornar no hacer nada
            break
        else:
            # Caso contrario, codificar la imagen como JPG
            _, buffer = cv2.imencode(".jpg", imagen)
            # pasar la imagen codificada a bytes 
            imagen = buffer.tobytes()
        
        yield (b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' + imagen + b'\r\n')

# Ahora se presenta todo el proceso anterior a través de la función camara_vivo que será insertada más adelante en el HTML
# creación de ruta
@app.route("/login/tablero/cam") 
def camara_vivo():
    # respuesta del servidor para servir la webcam o cámara del móvil.
    return Response(frames_gen(), mimetype='multipart/x-mixed-replace; boundary=frame')


#FUNCIÓN LIVE PARA LLAMAR A LA PLANTILLA ANALISIS_LIVE.HTML 
@app.route("/login/tablero/live") 
def live():
    # renderiza la plantilla del live.
    return render_template('analisis_live.html')



# Obtener frame de camara
def obtener_frame_camara():
    # camara detectada
    ok, frame = camara.read()
    # si no esta activa
    if not ok:
        # retornar no hacer nada
        return False, None
    # Caso contrario, codificar la imagen como JPG
    _, bufer = cv2.imencode(".jpg", frame)
    # pasar la imagen codificada a bytes 
    imagen = bufer.tobytes()
    return True, imagen


@app.route("/login/tablero/captura_live")
# Una vez que se toma la foto se procede a descargarla acorde a lo establecido en la función descargar_foto()
def captura_real():
    #mensaje para mostrar datos del procesamiento en interfaz de resultados
    dtp_cap = ''
    porc_cap = ''
    c_msg = ''
    b_msg = ''
    suma=0
    contador=0
    media=0
    # se llama a la función obtener_frame_camara y se lo almacena en la variable frame.
    ok, frame = camara.read() 
    # si no esta ok
    if not ok:
        # que aborte un error tipo 500.
        abort(500) 
    else:
        print('Proceso de análisis con imageai') 
        basepath = os.path.dirname (__file__) # ruta del archivo actual
        cv2.imwrite(os.path.join(basepath, 'static/image', 'cap_test.jpg'), frame) 
        # Instanciar el objeto CustomObjectDetection a la variable detector
        detector_cap = CustomObjectDetection()
        # el modelo a testear tipo YOLOv3
        detector_cap.setModelTypeAsYOLOv3()
        # ruta donde está el modelo entrenado
        detector_cap.setModelPath("detection_model-ex-025--loss-0032.000.h5")
        # ruta donde está el archivo de configuración json
        detector_cap.setJsonPath("detection_config.json")
        # guardar modelo
        detector_cap.loadModel()
        # entrada y salida de la imagen a evaluar
        detections = detector_cap.detectObjectsFromImage(input_image="static/image/cap_test.jpg", output_image_path="static/image/tratamiento/cap_detected.jpg")
        if not detections:
            dtp_cap="No se detectó la plaga"
            porc_cap="Null"
            b_msg="success"
            c_msg="white"
        else:
            for detection in detections:
                per_array = np.array([detection["percentage_probability"]])
                per_long = len(per_array)
                print(per_array)
                print(per_long)
                for i in range(per_long):
                    for c in range(per_long):
                        contador += 1
                        suma += per_array[i]
                        media = suma / contador
                        print("Promedio calculado: ",media)
                        porc_cap=round(media,2)
                        if porc_cap >= 70 and porc_cap <= 100:
                            c_msg="white"
                            b_msg="danger"
                            dtp_cap="Planta con afectación grave"
                        elif porc_cap > 0 and porc_cap <= 69:
                            b_msg="warning"
                            c_msg="dark"
                            dtp_cap="Planta con afectación moderada"
                        else:
                            print("Error en la detección")
        
        return render_template('cap_vivo.html', dtp_cap=dtp_cap,porc_cap=porc_cap,c_msg=c_msg, b_msg=b_msg)

'''
RUTAS PARA EL REDIRECCIONAMIENTO A LOS HTML MEDIANTE UNA FUNCIÓN DE PYTHON
''' 
#Variables para crear rutas del servidor
@app.route('/')     #ruta para página principal
def inicio():
    # renderiza la plantilla inicio.html
    return render_template('inicio.html')


'''
LOGIN DE LA APP
'''
# creación de ruta login y uso de los métodos GET (enrutado) y POST (envio de informacion mediante formulario)
@app.route('/login/', methods=['GET','POST'])
def login():
    # declaración de mensaje de salida en caso de errores
    msg = ''
    # Comprobar si existen solicitudes POST de "nombre de usuario" y "contraseña" (formulario enviado por el usuario)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        #  Creando variables para facilitar el acceso a la información que viene por POST
        username = request.form['username']
        password = request.form['password']
        # Comprobar si la cuenta existe usando MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM login WHERE usr_usuario = %s AND contra = %s', (username, password))
        # Obtener un registro y devolver el resultado
        resultado = cursor.fetchone()
        # Si la cuenta existe en la tabla cuenta de la base de datos
        if resultado:
            # Crear datos de sesión, podemos acceder a estos datos en otras rutas 
            session['loggedin'] = True
            session['id'] = resultado['id']
            session['username'] = resultado['usr_usuario']
            # Una vez, validados los datos se redirige a la página de inicio
            return redirect(url_for('tablero'))
        else:
            # La cuenta no existe o el nombre de usuario/contraseña es incorrecto 
            msg = 'Nombre de usuario o contraseña incorrectos - Vuelva a ingresarlos!'
    # renderiza la plantilla de login y trae consigo el mensaje de error.
    return render_template('login.html', msg=msg)

'''
CIERRE DE SESIÓN DE LA APP
'''
@app.route('/login/logout')
def logout():
    # Eliminar los datos de la sesión, esto hará que el usuario cierre la sesión 
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirigir a la plantilla de login (inicio de sesión)
   return redirect(url_for('login'))

@app.route('/login/registro/confirm', methods=['GET', 'POST'])
def confirm():
    # presentar la plantilla de confirmación
    return render_template('registro_conf.html')

'''
REGISTRO DE USUARIO
'''
# creación de ruta registro y uso de los métodos GET (enrutado) y POST (envio de informacion mediante formulario)
@app.route('/login/registro', methods=['GET', 'POST'])
def registro():
    # mensaje de salida para error
    msg = ''
    # captura lo que viene en el método POST username y password
    if request.method == 'POST' and 'name' in request.form and 'second' in request.form and 'username' in request.form and 'password' in request.form  and 'c_password' in request.form:
        # Creación de variables para facilitar el acceso a lo que viene por POST
        name = request.form['name']
        second = request.form['second']
        username = request.form['username']
        password = request.form['password']
        c_password = request.form['c_password']
        # Comprobar si la cuenta existe usando MySQL 
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # sentencia SQL para verificar si la cuenta ya existe en tabla cuenta.
        cursor.execute('SELECT * FROM login WHERE usr_usuario = %s', (username,))
        # Este método recupera la fila siguiente de un conjunto de resultados de consulta y devuelve una sola secuencia.
        resultado_c = cursor.fetchone()
        # Si la cuenta existe, mostrar las comprobaciones de validación
        if resultado_c:
            msg = '¡La cuenta ya existe!'
        # validación nombre de usuario con letras y números
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'El nombre de usuario debe contener sólo caracteres y números'
        # validación si los datos del formulario no fueron rellenados.
        elif not name or not second or not username or not password or not c_password:
            msg = 'Por favor, rellene el formulario'
        elif password != c_password:
            msg = 'Las contraseñas no coinciden - Vuelva a insertar sus datos'
            #return render_template('registro.html', msg_password=msg_password)
        else:
            # La cuenta no existe y los datos del formulario son válidos, ahora inserte una nueva cuenta en la tabla de cuentas 
            cursor.execute('INSERT INTO login VALUES (NULL, %s, %s, %s, %s, %s)', (name, second, username,password, c_password))
            # Este método envía una sentencia COMMIT al servidor MySQL, confirmando la transacción actual.
            mysql.connection.commit()
            # redireccionando a plantilla confirmación de registro.
            return redirect(url_for('confirm'))
    elif request.method == 'POST':
        #Si el formulario está vacío (sin datos)
        msg = '¡Por favor, rellene el formulario!' 
    # Show registration form with message (if any)
    return render_template('registro.html', msg=msg)


'''
TABLERO
'''

@app.route('/login/tablero')  #creación de ruta URL sobre objeto app
def tablero():
    # Comprobar si el usuario ha iniciado la sesión 
    if 'loggedin' in session:
        # El usuario ha iniciado la sesión y se le muestra la página de inicio 
        return render_template('tablero.html', username=session['username']) 
    # El usuario no ha iniciado la sesión redirige a la página de inicio de sesión 
    return redirect(url_for('login'))
    
'''
PÁGINA DE PERFIL (DATOS)
'''
@app.route('/login/perfil')
def perfil():
    # Comprobar si el usuario ha iniciado la sesión
    if 'loggedin' in session:
        # Vamos a consultar toda la información de la cuenta del usuario para poder mostrarla en la página del perfil
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        # consulta para tomar los datos del usuario por ID
        cursor.execute('SELECT * FROM login WHERE id = %s', (session['id'],))
        # recupera la fila de los datos del usuario
        resu_per = cursor.fetchone()
        # Mostrar la página de perfil con la información de la cuenta 
        return render_template('perfil.html', resu_per=resu_per) 
    # El usuario no ha iniciado la sesión redirige a la página de inicio de sesión 
    return redirect(url_for('login'))

'''
SUBIDA DE ARCHIVOS MANUALMENTE
'''
# Establecer el tiempo de caducidad de la caché de archivos estáticos
app.send_file_max_age_default = timedelta(seconds=1) 
 
@app.route ('/login/tablero/analisis', methods = ['POST', 'GET']) # agregar una ruta 
def subida():
    #mensaje para mostrar datos del procesamiento en interfaz de resultados
    dtp = ''
    porc = ''
    c_msg = ''
    b_msg = ''
    suma = 0
    contador = 0
    media = 0
    #sum_num=0
    # si existe u archivo mediante POST
    if request.method == 'POST':
        # pasando la imagen subida a la variable f
        f = request.files['file']
        # si el archivo subido no cumple con la extensión solicitada .jpg
        if not (f and allowed_file(f.filename)): 
            # retorna la plantilla de error
            return render_template('error.html')
        # caso contrario, toma el nombre de la imagen               
        user_input = request.form.get("name")
        basepath = os.path.dirname (__file__) # ruta del archivo actual 
        upload_path = os.path.join (basepath, 'static/image/drive', secure_filename (f.filename)) # Nota: primero debe crear una carpeta que no existe; de ​​lo contrario, se le indicará que no existe dicha ruta 
        #guardar la imagen
        f.save(upload_path)
        #Se convierte el formato y el nombre de la imagen
        img = cv2.imread(upload_path) 
        cv2.imwrite(os.path.join(basepath, 'static/image', 'test.jpg'), img)  #guardar la imagen con nombre test
        # Instanciar el objeto CustomObjectDetection a la variable detector
        detector = CustomObjectDetection()
        # el modelo a testear tipo YOLOv3
        detector.setModelTypeAsYOLOv3()
        # ruta donde está el modelo entrenado
        detector.setModelPath("detection_model-ex-025--loss-0032.000.h5")
        # ruta donde está el archivo de configuración json
        detector.setJsonPath("detection_config.json")
        # guardar modelo
        detector.loadModel()
        # entrada y salida de la imagen a evaluar
        detections = detector.detectObjectsFromImage(input_image="static/image/test.jpg", output_image_path="static/image/tratamiento/image_detected.jpg")
        if not detections:
            dtp="No se detectó la plaga"
            porc="Null"
            b_msg="success"
            c_msg="white"
        else:
            for detection in detections:
                per_array = np.array([detection["percentage_probability"]])
                per_long = len(per_array)
                print(per_array)
                print(per_long)
                for i in range(per_long):
                    for c in range(per_long):
                        contador += 1
                        suma += per_array[i]
                        media = suma / contador
                        print("Promedio calculado: ",media)
                        porc=round(media,2)
                        if porc >= 70 and porc <=100:
                            c_msg="white"
                            b_msg="danger"
                            dtp="Planta con afectación grave"
                        elif porc >0 and porc <=69:
                            b_msg="warning"
                            c_msg="dark"
                            dtp="Planta con afectación moderada"
                        else:
                            print("Error en la detección") 
        return render_template('subida_ok.html',userinput=user_input, dtp=dtp,porc=porc,c_msg=c_msg, b_msg=b_msg)
    # caso contrario, renderiza la plantilla de subida de archivo
    return render_template('subida.html')


#Validación para comprobar si estamos en el archivo principal
if __name__ == '__main__':
    app.run(port = PORT,debug=DEBUG) #ejecución de la app