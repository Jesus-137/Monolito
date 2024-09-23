from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import uuid

app = Flask(__name__)

# Configuración de la base de datos (usa tu configuración aquí)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:SoyYo123@localhost/monolito'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['JWT_SECRET_KEY'] = 'tu_clave_secreta_segura'  # Cambia esto por una clave secreta segura
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=1)  # El token JWT expira en 1 día

db = SQLAlchemy(app)
jwt = JWTManager(app)

# Modelos de la base de datos
class Usuario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(500))  # Asegúrate de que el tamaño es suficiente
    name = db.Column(db.String(100))
    phone = db.Column(db.String(15))
    fechas = db.Column(db.String(50))

    def __repr__(self):
        return f"<Usuario {self.email}>"


class Cliente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    name = db.Column(db.String(100))
    tipo = db.Column(db.String(50))
    phone = db.Column(db.String(15))
    fechas = db.Column(db.String(50))


class Publicacion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True)
    description = db.Column(db.String(200))
    client_id = db.Column(db.Integer, db.ForeignKey('cliente.id'))
    fechas = db.Column(db.String(50))
    cliente = db.relationship('Cliente', backref=db.backref('publicaciones', lazy=True))


# Registro de usuarios (opcional)
@app.route('/register', methods=['POST'])
def register():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    name = data.get('name')
    phone = data.get('phone')

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already registered'}), 400

    # Generar un UUID
    new_uuid = str(uuid.uuid4())
    hashed_password = generate_password_hash(password, method='pbkdf2:sha256')
    new_usuario = Usuario(uuid=new_uuid, email=email, password=hashed_password, name=name, phone=phone)

    db.session.add(new_usuario)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Login de usuarios
@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Buscar el usuario en la base de datos
    usuario = Usuario.query.filter_by(email=email).first()

    # Verificar las credenciales
    if not usuario or not check_password_hash(usuario.password, password):
        return jsonify({'error': 'Invalid email or password'}), 401

    # Crear el token JWT
    access_token = create_access_token(identity=usuario.id)

    return jsonify({
        'access_token': access_token,
        'usuario': {
            'id': usuario.id,
            'name': usuario.name,
            'email': usuario.email
        }
    }), 200


# Endpoint para obtener la lista de usuarios con fields, include, y autenticación
@app.route('/usuarios', methods=['GET'])
@jwt_required()
def get_usuarios():
    fields = request.args.get('fields')
    include = request.args.get('include')
    per_page = int(request.args.get('per_page', 10))
    page = int(request.args.get('page', 1))

    # Obtener la identidad del usuario autenticado
    current_user_id = get_jwt_identity()

    # Obtener la lista de usuarios
    usuarios = Usuario.query.paginate(page, per_page, False)
    
    result = []
    for usuario in usuarios.items:
        if fields:
            selected_fields = fields.split(',')
            user_data = {field: getattr(usuario, field) for field in selected_fields if hasattr(usuario, field)}
        else:
            user_data = {
                'id': usuario.id,
                'uuid': usuario.uuid,
                'name': usuario.name,
                'phone': usuario.phone,
                'fechas': usuario.fechas
            }

        if include:
            included_entities = include.split(',')
            if 'publicaciones' in included_entities:
                user_data['publicaciones'] = [{'id': pub.id, 'description': pub.description} for pub in usuario.publicaciones]

        result.append(user_data)
    
    return jsonify({
        'usuarios': result,
        'total': usuarios.total,
        'page': page,
        'per_page': per_page
    })


# Endpoint para obtener clientes con fields, include, y autenticación
@app.route('/clientes', methods=['POST'])
@jwt_required()
def create_cliente():
    data = request.json
    name = data.get('name')
    tipo = data.get('tipo')
    phone = data.get('phone')

    new_uuid = str(uuid.uuid4())
    new_cliente = Cliente(uuid=new_uuid, name=name, tipo=tipo, phone=phone)

    db.session.add(new_cliente)
    db.session.commit()

    return jsonify({'message': 'Client created successfully'}), 201



# Endpoint para obtener publicaciones con fields, include, y autenticación
@app.route('/publicaciones', methods=['POST'])
@jwt_required()
def create_publicacion():
    data = request.json
    description = data.get('description')
    client_id = data.get('client_id')

    new_uuid = str(uuid.uuid4())
    new_publicacion = Publicacion(uuid=new_uuid, description=description, client_id=client_id)

    db.session.add(new_publicacion)
    db.session.commit()

    return jsonify({'message': 'Publication created successfully'}), 201


# Creación de las tablas en la base de datos
if __name__ == '__main__':
    with app.app_context():  # Contexto de la aplicación
        db.create_all()  # Crear tablas en la base de datos
    app.run(debug=True)  # Iniciar la aplicación