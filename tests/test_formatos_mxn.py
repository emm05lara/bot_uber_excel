import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from extraer_uber import PATRON_DINERO, convertir_mxn_a_numero, parsear_fila


class TestFormatosIndividualesAceptados(unittest.TestCase):
    def test_formatos_aceptados(self):
        formatos = [
            "MXN 1,696.32",
            "-MXN 1,184.55",
            "MXN -1,184.55",
            "1,696.32 MXN",
            "-1,184.55 MXN",
            "MXN 0.00",
            "0.00 MXN",
        ]

        for formato in formatos:
            with self.subTest(formato=formato):
                self.assertIsNotNone(PATRON_DINERO.fullmatch(formato))


class TestConversiones(unittest.TestCase):
    def test_conversiones(self):
        casos = [
            ("MXN 1,696.32", 1696.32),
            ("-MXN 1,184.55", -1184.55),
            ("MXN -1,184.55", -1184.55),
            ("1,696.32 MXN", 1696.32),
            ("-1,184.55 MXN", -1184.55),
        ]

        for texto, esperado in casos:
            with self.subTest(texto=texto):
                self.assertAlmostEqual(convertir_mxn_a_numero(texto), esperado)


class TestFilaConPrefijoMXN(unittest.TestCase):
    def test_fila_prefijo(self):
        texto = (
            "Conductor Ejemplo\n"
            "MXN 1,696.32\n"
            "MXN 58.38\n"
            "MXN 0.00\n"
            "-MXN 1,184.55\n"
            "MXN 570.15"
        )

        fila = parsear_fila(texto)

        self.assertIsNotNone(fila)
        self.assertEqual(fila["Nombre del conductor"], "Conductor Ejemplo")
        self.assertAlmostEqual(fila["Ganancias totales"], 1696.32)
        self.assertAlmostEqual(fila["Reembolsos y gastos"], 58.38)
        self.assertAlmostEqual(fila["Ajustes"], 0.0)
        self.assertAlmostEqual(fila["Pago"], -1184.55)
        self.assertAlmostEqual(fila["Ganancias netas"], 570.15)


class TestFilaConSufijoMXN(unittest.TestCase):
    def test_fila_sufijo(self):
        texto = (
            "Conductor Ejemplo\n"
            "1,696.32 MXN\n"
            "58.38 MXN\n"
            "0.00 MXN\n"
            "-1,184.55 MXN\n"
            "570.15 MXN"
        )

        fila = parsear_fila(texto)

        self.assertIsNotNone(fila)
        self.assertEqual(fila["Nombre del conductor"], "Conductor Ejemplo")
        self.assertAlmostEqual(fila["Ganancias totales"], 1696.32)
        self.assertAlmostEqual(fila["Reembolsos y gastos"], 58.38)
        self.assertAlmostEqual(fila["Ajustes"], 0.0)
        self.assertAlmostEqual(fila["Pago"], -1184.55)
        self.assertAlmostEqual(fila["Ganancias netas"], 570.15)


class TestExactamenteCincoCantidades(unittest.TestCase):
    def test_cinco_cantidades_aceptadas(self):
        texto = (
            "Conductor Ejemplo\n"
            "MXN 1,696.32\n"
            "MXN 58.38\n"
            "MXN 0.00\n"
            "-MXN 1,184.55\n"
            "MXN 570.15"
        )

        self.assertIsNotNone(parsear_fila(texto))

    def test_cuatro_cantidades_rechazadas(self):
        texto = (
            "Conductor Ejemplo\n"
            "MXN 1,696.32\n"
            "MXN 58.38\n"
            "MXN 0.00\n"
            "-MXN 1,184.55"
        )

        self.assertIsNone(parsear_fila(texto))


class TestFormatosMezclados(unittest.TestCase):
    def test_formatos_mezclados(self):
        texto = (
            "Conductor Ejemplo\n"
            "MXN 1,696.32\n"
            "58.38 MXN\n"
            "MXN 0.00\n"
            "-1,184.55 MXN\n"
            "MXN 570.15"
        )

        cantidades = PATRON_DINERO.findall(texto)
        self.assertEqual(len(cantidades), 5)

        fila = parsear_fila(texto)
        self.assertIsNotNone(fila)


if __name__ == "__main__":
    unittest.main()
