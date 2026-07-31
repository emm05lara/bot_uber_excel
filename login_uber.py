from playwright.sync_api import sync_playwright

URL_UBER = "https://supplier.uber.com/orgs/375f1f6e-f932-49e8-96fb-34bd842346d9/earnings"

with sync_playwright() as p:
    contexto = p.chromium.launch_persistent_context(
        user_data_dir="perfil_uber",
        headless=False,
        viewport={"width": 1400, "height": 900},
    )

    pagina = contexto.new_page()
    pagina.goto(URL_UBER)

    print("\nInicia sesión manualmente en UBER.")
    print("Cuando ya estés dentro y veas tu panel, regresa aquí y presiona ENTER.\n")
    input("Presiona ENTER para cerrar y guardar la sesión...")

    contexto.close()