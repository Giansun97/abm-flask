from flask import Flask, render_template, request, redirect, url_for, send_file
import sqlite3
import pandas as pd


def consultar_tabla_clientes():
    # Conectar a la base de datos
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Obtener la lista de tablas en la base de datos
    cursor.execute("SELECT * FROM clientes")
    my_result = cursor.fetchall()
    insertObject = []
    columnNames = [column[0] for column in cursor.description]
    for record in my_result:
        insertObject.append(dict(zip(columnNames, record)))
        print(insertObject)

    # Cerrar la conexión
    conn.close()


consultar_tabla_clientes()


def agregar_cliente(cuit, password, nombre):
    """Agregar un nuevo cliente a la base de datos."""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    # Verificar si el cliente ya existe
    cursor.execute("SELECT * FROM clientes WHERE cuit=?", (cuit,))
    existing_client = cursor.fetchone()

    if existing_client:
        conn.close()
        return "El cliente ya se encuentra registrado en la base de datos."

    cursor.execute("INSERT INTO clientes (cuit, password, nombre) VALUES (?, ?, ?)", (cuit, password, nombre))
    conn.commit()
    conn.close()

    return "Cliente agregado exitosamente."


def obtener_todos_los_clientes():
    """Muestra todos los datos de los clientes en formato DataFrame"""
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes")
    clientes = cursor.fetchall()
    print(clientes)
    conn.close()

    return clientes

obtener_todos_los_clientes()


def actualizar_cliente(cuit, password, nombre):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()
    cursor.execute("UPDATE clientes SET password=?, nombre=? WHERE cuit=?", (password, nombre, cuit))
    conn.commit()
    conn.close()


app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def home():
    message = None

    if request.method == 'POST':
        cuit = request.form['cuit']
        password = request.form['password']
        nombre = request.form['nombre']
        message = agregar_cliente(cuit, password, nombre)

    clientes = obtener_todos_los_clientes()

    return render_template('home.html',
                           message=message,
                           clientes=clientes)


@app.route('/exportar_excel', methods=['GET'])
def exportar_excel():
    # Obtén la lista de clientes
    clientes = obtener_todos_los_clientes()

    # Crea un DataFrame con los clientes
    df = pd.DataFrame(clientes, columns=['Cuit', 'Password', 'Nombre',
                                         'Liquidador', 'Certificado MiPyme', 'Vencimiento'])

    # Exporta el DataFrame a un archivo Excel
    archivo_excel = 'clientes.xlsx'
    df.to_excel(archivo_excel, index=False, engine='xlsxwriter')

    return send_file(archivo_excel, as_attachment=True, download_name='clientes.xlsx')


@app.route('/cliente/<int:cuit>')
def ver_cliente(cuit):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        # Obtener el estado del certificado MiPyme desde el formulario
        tiene_certificado = request.form.get('tiene_certificado')
        # Actualizar el estado del certificado MiPyme en la base de datos
        cursor.execute("UPDATE clientes SET tiene_certificado = ? WHERE cuit = ?", (tiene_certificado, cuit))
        conn.commit()

    # Obtener los detalles del cliente por su ID
    cursor.execute("SELECT * FROM clientes WHERE cuit=?", (cuit,))
    cliente = cursor.fetchone()

    conn.close()

    return render_template('cliente.html',
                           cliente=cliente)


@app.route('/editar_cliente/<string:cuit>', methods=['GET', 'POST'])
def editar_cliente(cuit):
    conn = sqlite3.connect('test.db')
    cursor = conn.cursor()

    if request.method == 'POST':
        password = request.form['password']
        nombre = request.form['nombre']
        actualizar_cliente(cuit, password, nombre)

    # Obtener los detalles del cliente por su ID
    cursor.execute("SELECT * FROM clientes WHERE cuit=?", (cuit,))
    cliente = cursor.fetchone()

    conn.close()

    return render_template('editar_cliente.html', cliente=cliente)


@app.route('/actualizar_cliente/<string:cuit>', methods=['POST'])
def actualizar_cliente(cuit):
    if request.method == 'POST':
        # Obtener los nuevos datos del cliente del formulario
        nuevo_nombre = request.form['nombre']
        nueva_password = request.form['password']
        liquidador = request.form['liquidador']
        tiene_certificado = request.form['tiene_certificado']
        vencimiento_certificado = request.form['vencimiento_certificado']

        # Conectar a la base de datos
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()

        try:
            # Actualizar los datos del cliente en la base de datos
            cursor.execute("UPDATE clientes SET nombre=?, password=?, liquidador=?, tiene_certificado=?, "
                           "vencimiento_certificado=? WHERE cuit=?",
                           (nuevo_nombre, nueva_password, liquidador,
                            tiene_certificado, vencimiento_certificado, cuit))
            print(tiene_certificado, vencimiento_certificado)
            conn.commit()
            conn.close()

            # Redirigir al usuario a la página de detalles del cliente actualizada
            return redirect(f'/cliente/{cuit}')
        except Exception as e:
            # Manejar errores si ocurren durante la actualización
            conn.rollback()
            conn.close()
            return f"Error al actualizar: {str(e)}"



if __name__ == '__main__':
    app.run(debug=True)

