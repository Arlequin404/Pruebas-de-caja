import unittest
from app import app

class TestCajaBlancaCrearActa(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.post('/login', data={
            'email': 'aaortis@uce.edu.ec',
            'password': '56789'
        }, follow_redirects=True)

    def test_crear_acta(self):
        response = self.app.post('/crear/actas', data={
            'asunto': 'Acta prueba blanca',
            'observaciones': 'Caja blanca directa'
        }, follow_redirects=True)

        self.assertIn(b'Se ha registrado un nuevo', response.data)
        print("✅ Caja blanca: lógica de creación ejecutada correctamente.")

if __name__ == '__main__':
    unittest.main()
