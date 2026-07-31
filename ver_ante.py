from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from pathlib import Path
from datetime import datetime, timedelta
import pandas as pd
import argparse
import re


URL_TABLA_UBER = "https://drivers.uber.com/"  # Cambia esto por la URL exacta de la pantalla de Ganancias

COLUMNAS = [
    "Nombre del conductor",
    "Ganancias totales",
    "Reembolsos y gastos",
    "Ajustes",
    "Pago",
    "Ganancias netas",
]

PATRON_DINERO = re.compile(r"-?\d[\d.,]*\s*MXN", re.IGNORECASE)


def calcular_semana_anterior():
    """
    Si hoy es lunes 22/06/2026:
    devuelve inicio = 2026/06/15 y fin = 2026/06/21.
    """
    hoy = datetime.now().date()
    lunes_actual = hoy - timedelta(days=hoy.weekday())

    lunes_anterior = lunes_actual - timedelta(days=7)
    domingo_anterior = lunes_actual - timedelta(days=1)

    return (
        lunes_anterior.strftime("%Y/%m/%d"),
        domingo_anterior.strftime("%Y/%m/%d"),
    )


def normalizar_fecha(fecha):
    """
    Acepta:
    2026/06/15
    2026-06-15
    15/06/2026

    Devuelve:
    2026/06/15
    """
    formatos = ["%Y/%m/%d", "%Y-%m-%d", "%d/%m/%Y"]

    for formato in formatos:
        try:
            return datetime.strptime(fecha, formato).strftime("%Y/%m/%d")
        except ValueError:
            pass

    raise ValueError(f"Formato de fecha no válido: {fecha}")


def convertir_mxn_a_numero(texto):
    """
    Convierte:
    '5389,31 MXN' -> 5389.31
    '-3118,28 MXN' -> -3118.28
    '1.234,56 MXN' -> 1234.56
    """
    limpio = texto.replace("MXN", "").replace(" ", "").strip()

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
        "Saldo final",
        "Saldo inicial",
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
    ]

    if any(t in texto for t in textos_invalidos):
        return None

    cantidades = PATRON_DINERO.findall(texto)

    if len(cantidades) != 5:
        return None

    primera_cantidad = cantidades[0]
    posicion_primera_cantidad = texto.find(primera_cantidad)

    texto_antes = texto[:posicion_primera_cantidad].strip()
    lineas_antes = [linea.strip() for linea in texto_antes.splitlines() if linea.strip()]

    if lineas_antes:
        nombre = lineas_antes[-1]
    else:
        nombre = texto_antes

    nombre = limpiar_nombre(nombre)

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


def abrir_selector_fechas(pagina):
    """
    Intenta abrir el botón/píldora donde aparece el rango de fechas.
    """
    posibles_selectores = [
        r"\d{2}/\d{2}/\d{4}",
        r"\d{4}/\d{2}/\d{2}",
    ]

    for patron in posibles_selectores:
        try:
            elemento = pagina.get_by_text(re.compile(patron)).first
            elemento.click(timeout=5000)
            pagina.wait_for_timeout(1000)
            return True
        except Exception:
            pass

    posibles_css = [
        "button:has-text('/')",
        "[role='button']:has-text('/')",
        "div:has-text('/')",
    ]

    for selector in posibles_css:
        try:
            elemento = pagina.locator(selector).first
            elemento.click(timeout=5000)
            pagina.wait_for_timeout(1000)
            return True
        except Exception:
            pass

    return False


def seleccionar_rango_personalizado(pagina):
    """
    Da clic en la pestaña o botón de Rango personalizado.
    """
    posibles = [
        pagina.get_by_text("Rango personalizado", exact=False),
        pagina.get_by_role("tab", name=re.compile("Rango personalizado", re.IGNORECASE)),
        pagina.locator("text=Rango personalizado"),
    ]

    for elemento in posibles:
        try:
            elemento.first.click(timeout=5000)
            pagina.wait_for_timeout(1000)
            return True
        except Exception:
            pass

    return False


def llenar_fechas_con_javascript(pagina, fecha_inicio, fecha_fin):
    """
    Llena los dos inputs visibles de fecha.
    Usa JavaScript porque algunas páginas modernas no responden bien a .fill().
    """
    resultado = pagina.evaluate(
        """
        ({fechaInicio, fechaFin}) => {
            function esVisible(el) {
                const estilo = window.getComputedStyle(el);
                const rect = el.getBoundingClientRect();

                return (
                    estilo.display !== "none" &&
                    estilo.visibility !== "hidden" &&
                    rect.width > 0 &&
                    rect.height > 0
                );
            }

            function setValorReact(input, valor) {
                input.focus();

                const setter = Object.getOwnPropertyDescriptor(
                    window.HTMLInputElement.prototype,
                    "value"
                ).set;

                setter.call(input, valor);

                input.dispatchEvent(new Event("input", { bubbles: true }));
                input.dispatchEvent(new Event("change", { bubbles: true }));
                input.blur();
            }

            const todosInputs = Array.from(document.querySelectorAll("input"))
                .filter(esVisible);

            const regexFecha = /^\\d{4}[/-]\\d{2}[/-]\\d{2}$/;

            let inputsFecha = todosInputs.filter(input => {
                const valor = (input.value || "").trim();
                const placeholder = (input.placeholder || "").toLowerCase();
                const aria = (input.getAttribute("aria-label") || "").toLowerCase();

                return (
                    regexFecha.test(valor) ||
                    placeholder.includes("date") ||
                    placeholder.includes("fecha") ||
                    aria.includes("date") ||
                    aria.includes("fecha")
                );
            });

            if (inputsFecha.length < 2) {
                inputsFecha = todosInputs.slice(-2);
            }

            if (inputsFecha.length < 2) {
                return {
                    ok: false,
                    mensaje: "No se encontraron dos inputs de fecha visibles.",
                    inputsVisibles: todosInputs.map(i => ({
                        value: i.value,
                        placeholder: i.placeholder,
                        aria: i.getAttribute("aria-label")
                    }))
                };
            }

            setValorReact(inputsFecha[0], fechaInicio);
            setValorReact(inputsFecha[1], fechaFin);

            return {
                ok: true,
                inicio: inputsFecha[0].value,
                fin: inputsFecha[1].value
            };
        }
        """,
        {"fechaInicio": fecha_inicio, "fechaFin": fecha_fin},
    )

    return resultado


def confirmar_rango_fechas(pagina):
    """
    Intenta confirmar el rango.
    Dependiendo de Uber, puede llamarse Aplicar, Guardar, Actualizar, Done, etc.
    Si no existe botón, presiona Enter y Escape.
    """
    patron_boton = re.compile(
        r"Aplicar|Aceptar|Guardar|Actualizar|Apply|Done|Save|Update",
        re.IGNORECASE,
    )

    try:
        boton = pagina.get_by_role("button", name=patron_boton).first
        boton.click(timeout=3000)
        pagina.wait_for_timeout(2500)
        return
    except Exception:
        pass

    try:
        pagina.keyboard.press("Enter")
        pagina.wait_for_timeout(1000)
        pagina.keyboard.press("Escape")
        pagina.wait_for_timeout(2500)
    except Exception:
        pass


def aplicar_rango_personalizado(pagina, fecha_inicio, fecha_fin):
    print(f"\nAplicando rango personalizado: {fecha_inicio} a {fecha_fin}")

    abierto = abrir_selector_fechas(pagina)

    if not abierto:
        print("No pude abrir automáticamente el selector de fechas.")
        print("Abre manualmente el selector y deja visible la pestaña de Rango personalizado.")
        input("Cuando esté abierto, presiona ENTER para continuar...")

    personalizado = seleccionar_rango_personalizado(pagina)

    if not personalizado:
        print("No pude seleccionar automáticamente 'Rango personalizado'.")
        print("Selecciónalo manualmente.")
        input("Cuando esté seleccionado, presiona ENTER para continuar...")

    resultado = llenar_fechas_con_javascript(pagina, fecha_inicio, fecha_fin)

    if not resultado.get("ok"):
        print("No pude llenar automáticamente las fechas.")
        print(resultado)
        print("Llena manualmente las fechas en Uber.")
        input("Cuando estén listas, presiona ENTER para continuar...")
    else:
        print(f"Fechas colocadas: {resultado.get('inicio')} a {resultado.get('fin')}")

    confirmar_rango_fechas(pagina)

    print("Esperando actualización de la tabla...")
    pagina.wait_for_timeout(5000)


def extraer_candidatos_dom(pagina):
    """
    Busca elementos visibles que parezcan filas reales de la tabla.
    Se filtra por exactamente 5 valores MXN, porque cada fila tiene:
    ganancias, reembolsos, ajustes, pago y ganancias netas.
    """
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
            "Descargar informe"
        ];

        const all = Array.from(document.body.querySelectorAll("*"));
        const candidates = [];

        for (const el of all) {
            if (!isVisible(el)) continue;

            const inner = (el.innerText || "").replace(/\\u00a0/g, " ").trim();
            const raw = (el.textContent || "").replace(/\\u00a0/g, " ").trim();

            if (!inner && !raw) continue;

            const textForCount = inner || raw;

            if (blacklist.some(item => textForCount.includes(item))) continue;

            const count = moneyCount(textForCount);

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
                        text: inner || raw,
                        textContent: raw || inner,
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


def extraer_filas_pagina(pagina):
    candidatos = extraer_candidatos_dom(pagina)
    filas = []

    for candidato in candidatos:
        texto = candidato.get("textContent") or candidato.get("text")
        fila = parsear_fila(texto)

        if fila:
            filas.append(fila)

    return filas


def avanzar_siguiente_pagina(pagina):
    """
    Da clic en Siguiente si está disponible.
    """
    posibles = [
        pagina.get_by_role("button", name=re.compile("Siguiente", re.IGNORECASE)),
        pagina.locator("button:has-text('Siguiente')"),
        pagina.locator("[role='button']:has-text('Siguiente')"),
        pagina.locator("text=Siguiente"),
    ]

    for elemento in posibles:
        try:
            if elemento.count() == 0:
                continue

            boton = elemento.first

            deshabilitado = boton.evaluate(
                """
                el => {
                    const estilo = window.getComputedStyle(el);
                    const clase = String(el.className || "").toLowerCase();

                    return (
                        el.disabled === true ||
                        el.getAttribute("disabled") !== null ||
                        el.getAttribute("aria-disabled") === "true" ||
                        clase.includes("disabled") ||
                        clase.includes("disable") ||
                        Number(estilo.opacity) < 0.6 ||
                        estilo.pointerEvents === "none"
                    );
                }
                """
            )

            if deshabilitado:
                return False

            boton.click(timeout=5000)
            pagina.wait_for_timeout(2500)
            return True

        except Exception:
            pass

    return False


def extraer_todas_las_paginas(pagina, max_paginas=50):
    registros = {}

    for numero_pagina in range(1, max_paginas + 1):
        print(f"\nLeyendo página {numero_pagina}...")

        filas = extraer_filas_pagina(pagina)

        print(f"Filas encontradas en esta página: {len(filas)}")

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

        pudo_avanzar = avanzar_siguiente_pagina(pagina)

        if not pudo_avanzar:
            break

    return list(registros.values())


def guardar_debug(pagina, carpeta_salida, fecha_archivo):
    archivo_debug = carpeta_salida / f"debug_candidatos_{fecha_archivo}.txt"
    candidatos = extraer_candidatos_dom(pagina)

    with open(archivo_debug, "w", encoding="utf-8") as f:
        for i, candidato in enumerate(candidatos, start=1):
            f.write(f"\n--- CANDIDATO {i} ---\n")
            f.write(candidato.get("text", ""))
            f.write("\n")
            f.write("\nTEXT CONTENT:\n")
            f.write(candidato.get("textContent", ""))
            f.write("\n")

    return archivo_debug


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--url",
        default=URL_TABLA_UBER,
        help="URL exacta de la pantalla de Ganancias de Uber.",
    )

    parser.add_argument(
        "--inicio",
        default=None,
        help="Fecha inicial. Ejemplo: 2026/06/15",
    )

    parser.add_argument(
        "--fin",
        default=None,
        help="Fecha final. Ejemplo: 2026/06/21",
    )

    args = parser.parse_args()

    if args.inicio and args.fin:
        fecha_inicio = normalizar_fecha(args.inicio)
        fecha_fin = normalizar_fecha(args.fin)
    else:
        fecha_inicio, fecha_fin = calcular_semana_anterior()

    carpeta_salida = Path("salidas")
    carpeta_salida.mkdir(exist_ok=True)

    fecha_archivo = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    archivo_excel = carpeta_salida / f"ganancias_uber_{fecha_archivo}.xlsx"
    archivo_screenshot = carpeta_salida / f"captura_{fecha_archivo}.png"

    with sync_playwright() as p:
        contexto = p.chromium.launch_persistent_context(
            user_data_dir="perfil_uber",
            headless=False,
            viewport={"width": 1600, "height": 950},
        )

        pagina = contexto.new_page()

        print("\nAbriendo Uber...")
        pagina.goto(args.url)
        pagina.wait_for_timeout(6000)

        aplicar_rango_personalizado(pagina, fecha_inicio, fecha_fin)

        try:
            pagina.wait_for_selector("text=MXN", timeout=30000)
        except PlaywrightTimeoutError:
            print("\nNo encontré datos con MXN.")
            print("Verifica que la tabla esté visible.")
            pagina.screenshot(path=str(archivo_screenshot), full_page=True)
            contexto.close()
            return

        filas = extraer_todas_las_paginas(pagina)

        archivo_debug = guardar_debug(pagina, carpeta_salida, fecha_archivo)

        pagina.screenshot(path=str(archivo_screenshot), full_page=True)

        contexto.close()

    if not filas:
        print("\nNo se extrajeron filas.")
        print(f"Revisa el archivo debug: {archivo_debug}")
        print(f"Revisa la captura: {archivo_screenshot}")
        return

    df = pd.DataFrame(filas, columns=COLUMNAS)

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

    print("\nExtracción terminada.")
    print(f"Rango usado: {fecha_inicio} a {fecha_fin}")
    print(f"Filas extraídas: {len(df)}")
    print(f"Archivo Excel: {archivo_excel}")
    print(f"Archivo debug: {archivo_debug}")
    print(f"Captura: {archivo_screenshot}")


if __name__ == "__main__":
    main()