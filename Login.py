import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import json
import urllib.parse

class LoginBrowser:

    def __init__(self):
        self.profile_path = os.path.join(os.getcwd(), "chrome_profile")
        os.makedirs(self.profile_path, exist_ok=True)

        options = uc.ChromeOptions()
        options.add_argument(f"--user-data-dir={self.profile_path}")
        options.add_argument("--profile-directory=Default")

        # Evitar bugs comunes
        options.add_argument("--start-maximized")
        options.add_argument("--disable-gpu")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")

        self.driver = uc.Chrome(
            options=options,
            version_main=146,  # 👈 CLAVE: forzar versión correcta
            use_subprocess=True
        )
        self.wait = WebDriverWait(self.driver, 30)

    def open(self, url):
        print("Abriendo:", url)

        try:
            self.driver.get(url)
            time.sleep(3)

            # Fix página en blanco
            if self.driver.current_url in ["data:,", "about:blank"]:
                print("⚠️ Página en blanco, forzando carga...")
                self.driver.execute_script(f"window.open('{url}', '_self');")
                time.sleep(5)

        except Exception as e:
            print("Error al abrir, reintentando:", e)
            self.driver.execute_script(f"window.location.href = '{url}';")
            time.sleep(5)

        print("URL actual:", self.driver.current_url)

    def is_logged_in(self):
        try:
            element = self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                ".chatlist-top"
            )))

            if element.is_displayed():
                return True
            return False

        except:
            return False

    def wait_for_login(self):
        print("Esperando login en Telegram...")

        while True:
            if self.is_logged_in():
                print("✅ Sesión iniciada en Telegram")
                return True
            else:
                print("❌ No logueado aún...")
                time.sleep(3)

    def open_bot(self):
        bot_url = "https://web.telegram.org/k/#@BirdsEmpireBot"
        print("🚀 Abriendo bot:", bot_url)

        try:
            self.driver.get(bot_url)
            time.sleep(5)

            if "BirdsEmpireBot" not in self.driver.current_url:
                self.driver.execute_script(f"window.location.href = '{bot_url}';")
                time.sleep(1)

            self.driver.refresh()

            # Esperar que cargue el chat
            self.wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR, "div.input-message-container"
            )))
            print("✅ Chat del bot listo")

            # 🔥 Click en Play
            time.sleep(1.5)

            print("🎮 Buscando botón Play...")

            try:
                play_button = self.wait.until(EC.element_to_be_clickable((
                    By.CSS_SELECTOR,
                    ".new-message-bot-commands"
                )))

                self.driver.execute_script("arguments[0].click();", play_button)
                print("✅ Botón Play presionado")

            except Exception as e:
                print("❌ No se pudo hacer click en Play:", e)

            # 🔥 Confirmar Launch
            time.sleep(2)

            print("🟡 Verificando popup de confirmación...")

            try:
                launch_button = WebDriverWait(self.driver, 5).until(
                    EC.element_to_be_clickable((
                        By.XPATH,
                        "//button[.//span[text()='Launch']]"
                    ))
                )

                self.driver.execute_script("arguments[0].click();", launch_button)
                print("🚀 Bot lanzado (Launch presionado)")

            except:
                print("ℹ️ No apareció popup (continuando...)")

            # 🔥 NUEVO: EXTRAER TOKEN DEL IFRAME
            print("🔍 Buscando iframe con token...")

            iframe = WebDriverWait(self.driver, 15).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "iframe"))
            )

            src = iframe.get_attribute("src")
            print("📦 Iframe src encontrado")

            # Extraer tgWebAppData
            if "tgWebAppData=" in src:
                token_part = src.split("tgWebAppData=")[1].split("&tgWebAppVersion")[0]

                decoded = urllib.parse.unquote(token_part)

                print("🔑 Token extraído")

                # Guardar en JSON
                data = {
                    "raw": token_part,
                    "decoded": decoded
                }

                with open("telegram_token.json", "w", encoding="utf-8") as f:
                    json.dump(data, f, indent=4)

                print("💾 Token guardado en telegram_token.json")
                self.driver.quit()

            else:
                print("❌ No se encontró tgWebAppData en el iframe")

        except Exception as e:
            print("Error abriendo bot:", e)
    def wait_until_close(self):
        print("Navegador abierto. La sesión se guarda automáticamente.")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            pass

    def close(self):
        self.driver.quit()


