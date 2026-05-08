from flask import render_template 
from flask import url_for
from flask import Flask
from flask import request
from flask import jsonify
from markupsafe import escape
import json
from flask import session
from flask import redirect


app = Flask(__name__, template_folder='templates/_build')
#iniciar sesion
app.secret_key = "clave_secreta_domotica_123"
def leer_usuarios():
    try:
        with open('usuaris.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"admin": "1234"}

def leer_casas():
    try:
        with open('cases.json', 'r') as j:
            return json.load(j)
    except FileNotFoundError:
        return []
    
def get_casas_user(usuario):
    casas = leer_casas()
    for c in casas:
        if c['user'] == usuario:
            return c['cases']
    return []

def guardar_casas(datos_casas):
    with open('cases.json', 'w') as j:
        json.dump(datos_casas, j, indent=4)

def guardar_casas_user(usuario, casas_usuario):
    casas = leer_casas()
    for c in casas:
        if c['user'] == usuario:
            c['cases'] = casas_usuario
            with open('cases.json', 'w') as j:
                json.dump(casas, j, indent=4)
            return
    casas.append({'user': usuario, 'cases': casas_usuario})
    with open('cases.json', 'w') as j:
        json.dump(casas, j, indent=4)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        usuario_introducido = request.form['usuario']
        clave_introducida = request.form['contrasena']
        
        usuarios = leer_usuarios()
        
        if usuario_introducido in usuarios and usuarios[usuario_introducido] == clave_introducida:
            session['usuario_actual'] = usuario_introducido # Creamos la cookie
            return redirect(url_for('inici'))
        else:
            error = "Usuario o contraseña incorrectos."
            
    return render_template('login.html', error=error)

@app.route('/logout')
def logout():
    session.pop('usuario_actual', None) # Eliminar las cookies
    return redirect(url_for('login'))

@app.route("/")
@app.route("/inici.html")
def inici():
    if 'usuario_actual' not in session:
        return redirect(url_for('login'))

    nombre_usuario = session['usuario_actual']    
    lista_casas = get_casas_user(nombre_usuario)
    return render_template('inici.html', nom=nombre_usuario, casas=lista_casas)

@app.route('/casas', methods=['POST'])
def create_casa():
    data = request.get_json() # obtener información del cuerpo de la solicitud
    name=data.get('nom')
    usuario_actual = session['usuario_actual']
    casas = get_casas_user(usuario_actual)

    if len(casas) > 0:
        # Busca el ID más alto en la lista actual y le suma 1
        nuevo_id = max(casa['id'] for casa in casas) + 1
    else:
        # Si por algún motivo la lista se queda vacía, empieza en 1
        nuevo_id = 1

    nova_casa={'id': nuevo_id, 'nom': name, 'habitacions': []}
    casas.append(nova_casa)
    guardar_casas_user(usuario_actual, casas)
    return jsonify(nova_casa), 201   

@app.route("/casa<int:casa_id>.html")
def veure_casa(casa_id):
    if 'usuario_actual' not in session:
        return redirect(url_for('login'))

    usuario_actual = session['usuario_actual']
    casas = get_casas_user(usuario_actual)

    #Buscamos cuál es la casa que el usuario ha clicado
    casa_actual = None
    for c in casas:
        if c['id'] == casa_id:
            casa_actual = c
            break

    #Si la casa existe, cargamos la plantilla y le pasamos los datos
    if casa_actual:
        return render_template('casa_plantilla.html', casa=casa_actual, casas=casas)
    else:
        return render_template('inici.html', casas=casas)

@app.route('/casas/<int:casa_id>/habitacions', methods=['POST'])
def create_habitacio(casa_id):
    data = request.get_json()
    nom_hab = data.get('nom')
    planta_hab = data.get('planta', '')

    usuario_actual = session['usuario_actual']
    casas = get_casas_user(usuario_actual)

    habitacio_creada = None

    for casa in casas:
        if casa['id'] == casa_id:
            # Calculamos el ID de la nueva habitación
            if len(casa['habitacions']) > 0:
                nuevo_id_hab = max(hab['id'] for hab in casa['habitacions']) + 1
            else:
                nuevo_id_hab = 1
            
            nova_habitacio = {
                'id': nuevo_id_hab,
                'nom': nom_hab,
                'planta': planta_hab,
                'dispositius': []
            }
            
            # La metemos dentro de la casa
            casa['habitacions'].append(nova_habitacio)
            habitacio_creada = nova_habitacio
            break

    # Guardamos todo
    if habitacio_creada:
        guardar_casas_user(usuario_actual, casas)
        return jsonify(habitacio_creada), 201
    else:
        return jsonify({"error": "No se ha encontrado la casa"}), 404
    
@app.route("/casa<int:casa_id>/habitacio<int:hab_id>.html")
def veure_habitacio(casa_id, hab_id):
    if 'usuario_actual' not in session:
        return redirect(url_for('login'))
    usuario_actual = session['usuario_actual']
    casas = get_casas_user(usuario_actual)

    casa_actual = None
    habitacio_actual = None

    for c in casas:
        if c['id'] == casa_id:
            casa_actual = c
            # Buscamos la habitación dentro de esa casa
            for h in c.get('habitacions', []):
                if h['id'] == hab_id:
                    habitacio_actual = h
                    break
            break

    # Si encontramos tanto la casa como la habitación, cargamos el molde
    if casa_actual and habitacio_actual:
        return render_template('habitacio_plantilla.html', casas=casas, casa=casa_actual, habitacio=habitacio_actual)
    else:
        return render_template('inici.html', casas=casas)
    
@app.route('/casas/<int:casa_id>/habitacions/<int:hab_id>/dispositius', methods=['POST'])
def create_dispositiu(casa_id, hab_id):
    data = request.get_json()
    nom_disp = data.get('nom')
    tipus_disp = data.get('tipus')

    # Abrimos la despensa
    usuario_actual = session['usuario_actual']
    casas = get_casas_user(usuario_actual)

    dispositiu_creat = None

    # Buscamos la casa
    for casa in casas:
        if casa['id'] == casa_id:
            # Buscamos la habitación dentro de la casa
            for hab in casa.get('habitacions', []):
                if hab['id'] == hab_id:
                    
                    # Seguro por si la lista de dispositivos no existe
                    if 'dispositius' not in hab:
                        hab['dispositius'] = []
                    
                    # Calculamos el ID del nuevo dispositivo
                    if len(hab['dispositius']) > 0:
                        nuevo_id_disp = max(d['id'] for d in hab['dispositius']) + 1
                    else:
                        nuevo_id_disp = 1
                    
                    # Preparamos el dispositivo
                    nou_dispositiu = {
                        'id': nuevo_id_disp,
                        'nom': nom_disp,
                        'tipus': tipus_disp,
                        'estat': 'OFF' # Le ponemos un estado inicial apagado por defecto
                    }
                    
                    # Lo guardamos en la habitación
                    hab['dispositius'].append(nou_dispositiu)
                    dispositiu_creat = nou_dispositiu
                    break
            break

    # Guardamos en el JSON y avisamos de que todo ha ido bien
    if dispositiu_creat:
        guardar_casas_user(usuario_actual, casas)
        return jsonify(dispositiu_creat), 201
    else:
        return jsonify({"error": "No se ha trobat l'habitació"}), 404
    
@app.route('/casas/<int:casa_id>/habitacions/<int:hab_id>/dispositius/<int:disp_id>/toggle', methods=['POST'])
def toggle_dispositiu(casa_id, hab_id, disp_id):
    usuario_actual = session['usuario_actual']
    casas = get_casas_user(usuario_actual)
    
    for casa in casas:
        if casa['id'] == casa_id:
            for hab in casa.get('habitacions', []):
                if hab['id'] == hab_id:
                    for disp in hab.get('dispositius', []):
                        if disp['id'] == disp_id:
                            
                            # MAGIA: Si estaba en ON, lo pasa a OFF. Y viceversa.
                            if disp.get('estat') == 'ON':
                                disp['estat'] = 'OFF'
                            else:
                                disp['estat'] = 'ON'
                                
                            # Guardamos en el disco duro
                            usuario_actual = session['usuario_actual']
                            guardar_casas_user(usuario_actual, casas)
                            return jsonify(disp), 200
                            
    return jsonify({"error": "Dispositiu no trobat"}), 404

@app.route("/perfil.html")
def perfil():
    if 'usuario_actual' not in session:
        return redirect(url_for('login'))
    return render_template('perfil.html', nom=session['usuario_actual'], casas=len(get_casas_user(session['usuario_actual'])))

@app.route("/afegir_casa.html")
def formulari():
    return render_template('afegir_casa.html')


@app.route('/casas', methods=['GET'])
def get_casas():
    if 'usuario_actual' not in session:
        return jsonify({"error": "No autenticado"}), 401
    casas = get_casas_user(session['usuario_actual'])
    return jsonify(casas), 200

@app.route('/casas/<int:casas_id>', methods=['GET'])
def get_casaid(casas_id):
    if 'usuario_actual' not in session:
        return jsonify({"error": "No autenticado"}), 401
    casas = get_casas_user(session['usuario_actual'])
    return jsonify(casas[casas_id-1]), 200

 


if __name__ == "__main__":
    app.run(debug=True)
