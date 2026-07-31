from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path
from datetime import datetime
import pandas as pd
import argparse
import re


URL_UBER = "https://drivers.uber.com/"

COLUMNAS = [
    "Nombre del conductor",
    "Ganancias totales",
    "Reembolsos y gastos",
    "Ajustes",
    "Pago",
    "Ganancias netas",
]

PATRON_DINERO = re.compile(r"-?\d[\d.,]*\s*MXN", re.IGNORECASE)


def convertir_mxn_a_numero(texto):
    limpio = texto.replace("MXN", "").replace("mxn", "").replace(" ", "").strip()

    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        limpio = limpio.replace(",", ".")

    try:
        return float(limpio)
    except ValueError:
        return None


def limpiar_nombre(nombre):
    textos_a_quitar = [
        "Nombre del conductor",
        "Ganancias totales",
        "Reembolsos y gastos",
        "Ajustes",
        "Pago",
        "Ganancias netas",
        "Ganancias del conductor",
    ]

    nombre = nombre.replace("›", "").replace(">", "").strip()

    for texto in textos_a_quitar:
        nombre = nombre.replace(texto, "")

    nombre = re.sub(r"\s+", " ", nombre).strip()
    return nombre


def parsear_fila(texto):
    texto = texto.replace("\u00a0", " ").strip()

    textos_invalidos = [
        "Saldo inicial",
        "Saldo final",
        "Ajustes de periodos anteriores",
        "Start Date",
        "End Date",
        "Rango personalizado",
        "Plazo de liquidación",
        "Descargar informe",
        "Instala nuestra app móvil",
        "Nombre del conductor Ganancias totales",
    ]

    if any(t in texto for t in textos_invalidos):
        return None

    cantidades = PATRON_DINERO.findall(texto)

    if len(cantidades) != 5:
        return None

    primera_cantidad = cantidades[0]
    posicion = texto.find(primera_cantidad)

    texto_antes = texto[:posicion].strip()
    lineas = [linea.strip() for linea in texto_antes.splitlines() if linea.strip()]

    if not lineas:
        return None

    nombre = limpiar_nombre(lineas[-1])

    if not nombre:
        return None

    return {
        "Nombre del conductor": nombre,
        "Ganancias totales": convertir_mxn_a_numero(cantidades[0]),
        "Reembolsos y gastos": convertir_mxn_a_numero(cantidades[1]),
        "Ajustes": convertir_mxn_a_numero(cantidades[2]),
        "Pago": convertir_mxn_a_numero(cantidades[3]),
        "Ganancias netas": convertir_mxn_a_numero(cantidades[4]),
    }


def extraer_candidatos_dom(pagina):
    script = """
    () => {
        const moneyRegex = /-?\\d[\\d.,]*\\s*MXN/g;

        function isVisible(el) {
            const style = window.getComputedStyle(el);
            const rect = el.getBoundingClientRect();

            return (
                style &&
                style.visibility !== "hidden" &&
                style.display !== "none" &&
                rect.width > 0 &&
                rect.height > 0
            );
        }

        function moneyCount(text) {
            const matches = text.match(moneyRegex);
            return matches ? matches.length : 0;
        }

        const blacklist = [
            "Saldo inicial",
            "Saldo final",
            "Ajustes de periodos anteriores",
            "Start Date",
            "End Date",
            "Rango personalizado",
            "Plazo de liquidación",
            "Descargar informe",
            "Instala nuestra app móvil"
        ];

        const all = Array.from(document.body.querySelectorAll("*"));
        const candidates = [];

        for (const el of all) {
            if (!isVisible(el)) continue;

            const inner = (el.innerText || "").replace(/\\u00a0/g, " ").trim();
            const raw = (el.textContent || "").replace(/\\u00a0/g, " ").trim();
            const text = inner || raw;

            if (!text) continue;
            if (blacklist.some(item => text.includes(item))) continue;

            const count = moneyCount(text);

            if (count === 5) {
                const children = Array.from(el.children || []);

                const childWithSamePattern = children.some(child => {
                    const childText = (child.innerText || child.textContent || "")
                        .replace(/\\u00a0/g, " ")
                        .trim();

                    return moneyCount(childText) === 5;
                });

                if (!childWithSamePattern) {
                    const rect = el.getBoundingClientRect();

                    candidates.push({
                        text: text,
                        tag: el.tagName,
                        x: rect.x,
                        y: rect.y,
                        width: rect.width,
                        height: rect.height
                    });
                }
            }
        }

        return candidates.sort((a, b) => a.y - b.y);
    }
    """

    return pagina.evaluate(script)


def extraer_filas_visibles(pagina):
    candidatos = extraer_candidatos_dom(pagina)
    filas = []

    for candidato in candidatos:
        fila = parsear_fila(candidato["text"])

        if fila:
            filas.append(fila)

    return filas, candidatos


def guardar_debug(candidatos, archivo_debug):
    with open(archivo_debug, "w", encoding="utf-8") as f:
        for i, candidato in enumerate(candidatos, start=1):
            f.write(f"\n--- CANDIDATO {i} ---\n")
            f.write(f"TAG: {candidato.get('tag')}\n")
            f.write(f"X: {candidato.get('x')} | Y: {candidato.get('y')}\n")
            f.write(candidato.get("text", ""))
            f.write("\n")


def guardar_excel(registros, archivo_excel):
    df = pd.DataFrame(registros, columns=COLUMNAS)

    columnas_monedas = [
        "Ganancias totales",
        "Reembolsos y gastos",
        "Ajustes",
        "Pago",
        "Ganancias netas",
    ]

    for columna in columnas_monedas:
        df[columna] = pd.to_numeric(df[columna], errors="coerce")

    df.to_excel(archivo_excel, index=False)


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        default=URL_UBER,
        help="URL exacta de la pantalla de Ganancias de Uber.",
    )

    args = parser.parse_args()

    carpeta_salida = Path("salidas")
    carpeta_salida.mkdir(exist_ok=True)

    fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archivo_excel = carpeta_salida / f"ganancias_uber_{fecha_archivo}.xlsx"
    archivo_debug = carpeta_salida / f"debug_candidatos_{fecha_archivo}.txt"
    archivo_captura = carpeta_salida / f"captura_{fecha_archivo}.png"

    registros = {}

    with sync_playwright() as p:
        contexto = p.chromium.launch_persistent_context(
            user_data_dir="perfil_uber",
            headless=False,
            viewport={"width": 1600, "height": 950},
        )

        pagina = contexto.new_page()

        print("\nAbriendo Uber...")
        pagina.goto(args.url)
        pagina.wait_for_load_state("domcontentloaded")

        print("\nInstrucciones:")
        print("1. Inicia sesión si Uber te lo pide.")
        print("2. Entra manualmente a la pestaña Ganancias.")
        print("3. Selecciona manualmente Rango personalizado.")
        print("4. Coloca las fechas que quieras consultar.")
        print("5. Selecciona cuántas filas quieres visualizar.")
        print("6. Cuando la tabla esté lista, vuelve a esta terminal y presiona ENTER.\n")

        input("Presiona ENTER cuando la tabla de ganancias esté visible y lista...")

        try:
            pagina.wait_for_selector("text=MXN", timeout=10000)
        except PlaywrightTimeoutError:
            print("\nNo encontré valores con MXN en pantalla.")
            print("Verifica que la tabla esté visible antes de presionar ENTER.")
            pagina.screenshot(path=str(archivo_captura), full_page=True)
            contexto.close()
            return

        while True:
            filas, candidatos = extraer_filas_visibles(pagina)

            print(f"\nFilas detectadas en esta vista: {len(filas)}")

            for fila in filas:
                clave = (
                    fila["Nombre del conductor"],
                    fila["Ganancias totales"],
                    fila["Reembolsos y gastos"],
                    fila["Ajustes"],
                    fila["Pago"],
                    fila["Ganancias netas"],
                )

                registros[clave] = fila

            print(f"Filas acumuladas sin duplicados: {len(registros)}")

            guardar_debug(candidatos, archivo_debug)
            pagina.screenshot(path=str(archivo_captura), full_page=True)

            print("\nOpciones:")
            print("ENTER  -> Ya cambié de página, filas o filtro; capturar otra vista")
            print("fin    -> Terminar y guardar Excel")
            print("limpiar-> Borrar acumulado y empezar de nuevo")

            opcion = input("\nEscribe una opción: ").strip().lower()

            if opcion == "fin":
                break

            if opcion == "limpiar":
                registros.clear()
                print("Acumulado limpiado.")
                input("Ajusta la tabla nuevamente y presiona ENTER para capturar...")
            else:
                input("Ajusta manualmente la tabla y presiona ENTER para capturar...")

        contexto.close()

    if not registros:
        print("\nNo se guardó nada porque no se detectaron filas.")
        print(f"Debug: {archivo_debug}")
        print(f"Captura: {archivo_captura}")
        return

    guardar_excel(list(registros.values()), archivo_excel)

    print("\nExtracción terminada.")
    print(f"Filas guardadas: {len(registros)}")
    print(f"Excel: {archivo_excel}")
    print(f"Debug: {archivo_debug}")
    print(f"Captura: {archivo_captura}")


if __name__ == "__main__":
    main()