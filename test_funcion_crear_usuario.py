import unittest
from app import crear_usuario_directo

class TestCrearUsuarioLogic(unittest.TestCase):
    def test_crear_usuario_post(self):
        usuario = crear_usuario_directo("Test Caja Blanca", "blanca@correo.com", "1234", "usuario")
        self.assertIsNotNone(usuario)
        self.assertEqual(usuario[1], "Test Caja Blanca")
        self.assertEqual(usuario[2], "blanca@correo.com")
        self.assertEqual(usuario[3], "1234")
        self.assertEqual(usuario[4], "usuario")

if __name__ == '__main__':
    unittest.main()
