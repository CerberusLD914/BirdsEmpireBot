import requests
import json
import time
import ctypes
import random
import os

ctypes.windll.kernel32.SetThreadExecutionState(0x80000002)

from Login import LoginBrowser

BASE_URL = "https://birdsbot.website/api/v1"


class BirdsBot:

    def __init__(self):
        self.token = None
        self.headers = None

        self.EGGS_TO_SILVER = 100

        # ⏱ control de venta
        self.next_sell_time = time.time() + random.randint(1, 60)

        # 🎯 objetivo bloqueado
        self.target_bird = None
        self.target_eta = None

        self.birds_data = {
            "birds_a": {"cost": 1000, "prod": 42},
            "birds_b": {"cost": 5000, "prod": 221},
            "birds_c": {"cost": 25000, "prod": 1160},
            "birds_d": {"cost": 125000, "prod": 6091},
            "birds_e": {"cost": 625000, "prod": 31979}
        }

        self.ensure_token()

    # ================= TOKEN =================

    def load_token(self):
        try:
            with open("telegram_token.json", "r", encoding="utf-8") as f:
                return json.load(f)["decoded"]
        except:
            return None

    def update_headers(self):
        self.headers = {
            "Authorization": f"tma {self.token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    def ensure_token(self):
        token = self.load_token()
        if not token:
            self.generate_new_token()
        else:
            self.token = token
            self.update_headers()

    def generate_new_token(self):
        print("🔐 Generando token.")

        bot = LoginBrowser()
        bot.open("https://web.telegram.org/k/")

        if not bot.is_logged_in():
            bot.wait_for_login()

        bot.open_bot()

        time.sleep(10)
        bot.driver.quit()

        self.token = self.load_token()
        self.update_headers()

    def is_token_expired(self, r):
        if not r:
            return False
        if r.status_code in [401, 403]:
            return True

        try:
            txt = str(r.json()).lower()
            return any(x in txt for x in ["unauthorized", "invalid", "expired"])
        except:
            return False

    def safe_request(self, method, url, **kwargs):
        r = requests.request(method, url, headers=self.headers, **kwargs)

        if self.is_token_expired(r):
            print("\n🔴 Token expirado → regenerando")
            self.generate_new_token()
            r = requests.request(method, url, headers=self.headers, **kwargs)

        return r

    # ================= API =================

    def get_account(self):
        r = self.safe_request("GET", f"{BASE_URL}/users/account")
        return r.json() if r else None

    def sell_eggs(self):
        return self.safe_request("POST", f"{BASE_URL}/warehouse/sell_eggs")

    def buy_bird(self, bird, qty):
        r = self.safe_request(
            "POST",
            f"{BASE_URL}/warehouse/buy_birds",
            json={bird: qty}
        )

        if r and r.status_code == 200:
            print(f"\n🐦 COMPRA: {bird} x{qty}")
            return r.json()

        return None

    # ================= CALCULO =================

    def silver_per_sec(self, prod):
        return (prod / self.EGGS_TO_SILVER) / 3600

    def choose_target_bird(self, silver, eggs, prod):
        effective = silver + (eggs / self.EGGS_TO_SILVER)
        income_sec = self.silver_per_sec(prod)

        MAX_WAIT = 3600  # 1 hora

        best = None
        best_cost = -1
        best_time = None

        fallback = None
        fallback_time = float("inf")

        for bird, data in self.birds_data.items():
            cost = data["cost"]

            missing = max(0, cost - effective)
            time_to_buy = missing / income_sec if income_sec > 0 else float("inf")

            # Mejor pájaro alcanzable dentro del tiempo máximo
            if time_to_buy <= MAX_WAIT:
                if cost > best_cost:
                    best = bird
                    best_cost = cost
                    best_time = time_to_buy

            # Si ninguno entra en MAX_WAIT, usar el más cercano
            if time_to_buy < fallback_time:
                fallback = bird
                fallback_time = time_to_buy

        if best:
            return best, best_time

        return fallback, fallback_time

    def format_time(self, seconds):
        if seconds == float("inf"):
            return "∞"

        seconds = int(seconds)

        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        elif seconds < 86400:
            return f"{seconds // 3600}h {(seconds % 3600) // 60}m"
        else:
            return f"{seconds // 86400}d {(seconds % 86400) // 3600}h"

    # ================= UI =================

    def clear_console(self):
        os.system("cls" if os.name == "nt" else "clear")

    def print_dashboard(self, eggs, silver, prod, best, eta):
        self.clear_console()

        print("🚀 BIRDS BOT OPTIMIZADO\n")
        print("📊 RECURSOS")
        print(f"🥚 Eggs   : {int(eggs)}")
        print(f"💰 Silver : {int(silver)}")
        print(f"⚙️ Prod/h : {int(prod)}")

        print("\n🧠 DECISIÓN")
        if best:
            print(f"🐦 Objetivo fijo : {best}")
            print(f"⏳ ETA           : {self.format_time(eta)}")
        else:
            print("⏳ Esperando oportunidad...")

        restante_venta = int(self.next_sell_time - time.time())
        if restante_venta > 0:
            print(f"\n💱 Próxima venta en: {restante_venta}s")
        else:
            print("\n💱 Venta lista")

    # ================= LOOP =================

    def run(self):
        print("🚀 Iniciando bot...\n")

        while True:
            try:
                acc = self.get_account()
                if not acc:
                    time.sleep(3)
                    continue

                eggs = acc["amount_eggs"]
                silver = acc["amount_silver"]
                prod = acc["total_productivity"]

                # Si no hay objetivo fijado, se elige uno y se bloquea
                if self.target_bird is None:
                    self.target_bird, self.target_eta = self.choose_target_bird(silver, eggs, prod)

                # 💱 venta con delay aleatorio
                if time.time() >= self.next_sell_time:
                    if eggs >= self.EGGS_TO_SILVER:
                        r = self.sell_eggs()
                        if r:
                            data = r.json()
                            eggs = data["amount_eggs"]
                            silver = data["amount_silver"]

                    self.next_sell_time = time.time() + random.randint(1, 20)

                # recalcular ETA del objetivo actual SIN cambiar objetivo
                if self.target_bird:
                    cost = self.birds_data[self.target_bird]["cost"]
                    effective = silver + (eggs / self.EGGS_TO_SILVER)
                    missing = max(0, cost - effective)
                    income_sec = self.silver_per_sec(prod)

                    self.target_eta = missing / income_sec if income_sec > 0 else float("inf")

                    # SOLO compra el objetivo fijado
                    qty = int(silver // cost)

                    if qty > 0:
                        acc = self.buy_bird(self.target_bird, qty)
                        if acc:
                            # liberar objetivo tras compra
                            self.target_bird = None
                            self.target_eta = None
                            continue

                self.print_dashboard(eggs, silver, prod, self.target_bird, self.target_eta)

                time.sleep(0.1)

            except Exception as e:
                print("\n❌ Error:", e)
                time.sleep(5)


if __name__ == "__main__":
    BirdsBot().run()