import unittest
import json
from Monolito import app, db, Usuario  # Asegúrate de importar tu aplicación y base de datos correctamente

class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:SoyYo123@localhost/monolito'
        self.client = self.app.test_client()
        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_register(self):
        response = self.client.post('/register', data=json.dumps({
            'email': 'test@example.com',
            'password': 'password',
            'name': 'Test User',
            'phone': '123456789'
        }), content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('User registered successfully', response.get_data(as_text=True))

    def test_login(self):
        # Primero registramos un usuario
        self.client.post('/register', data=json.dumps({
            'email': 'test@example.com',
            'password': 'password',
            'name': 'Test User',
            'phone': '123456789'
        }), content_type='application/json')

        # Luego intentamos loguearnos
        response = self.client.post('/login', data=json.dumps({
            'email': 'test@example.com',
            'password': 'password'
        }), content_type='application/json')

        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.get_json())

        # Guardar el token para pruebas posteriores
        self.access_token = response.get_json()['access_token']

    def test_get_usuarios(self):
        # Asegúrate de que el login se haya realizado para obtener el token
        if not hasattr(self, 'access_token'):
            self.test_login()  # Ejecutar test_login si no se ha guardado el token

        response = self.client.get('/usuarios', headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('usuarios', response.get_json())

    def test_get_clientes(self):
        # Asegúrate de que el login se haya realizado para obtener el token
        if not hasattr(self, 'access_token'):
            self.test_login()  # Ejecutar test_login si no se ha guardado el token

        response = self.client.get('/clientes', headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('clientes', response.get_json())

    def test_get_publicaciones(self):
        # Asegúrate de que el login se haya realizado para obtener el token
        if not hasattr(self, 'access_token'):
            self.test_login()  # Ejecutar test_login si no se ha guardado el token

        response = self.client.get('/publicaciones', headers={'Authorization': f'Bearer {self.access_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('publicaciones', response.get_json())

if __name__ == '__main__':
    unittest.main()
