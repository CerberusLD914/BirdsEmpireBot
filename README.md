# 🐦 BirdsEmpireBot

Bot automatizado para el juego **BirdsEmpire (Telegram WebApp)** que optimiza la recolección de huevos, conversión a silver y compra inteligente de aves.

---

## 🚀 Características

* 🔐 Autenticación automática usando Telegram Web
* 🧠 Sistema inteligente de compra de aves
* 💱 Venta automática de huevos con delay aleatorio (anti-spam)
* 📊 Dashboard en consola limpio (sin spam)
* 🔄 Manejo automático de expiración de token
* ⚡ Loop rápido optimizado (0.1s)

---

## 🧱 Estructura del Proyecto

```
BirdsEmpireBot/
│
├── bot.py                # Lógica principal del bot
├── Login.py             # Manejo de login + extracción de token
├── telegram_token.json  # Token guardado automáticamente
├── chrome_profile/      # Perfil persistente de Chrome
└── README.md            # Este archivo
```

---

## ⚙️ Requisitos

* Python 3.10+
* Google Chrome (versión compatible)

### 📦 Librerías necesarias

Instalar con:

```
pip install requests selenium undetected-chromedriver
```

---

## 🔐 Funcionamiento del Login

El bot utiliza Selenium + undetected_chromedriver para:

1. Abrir Telegram Web
2. Esperar login manual (solo la primera vez)
3. Abrir @BirdsEmpireBot
4. Presionar "Play" y "Launch"
5. Extraer el parámetro `tgWebAppData` desde un iframe
6. Guardarlo en `telegram_token.json`

Luego el bot reutiliza ese token automáticamente.

---

## 🧠 Lógica del Bot

### 1. Obtención de datos

Consulta continuamente:

* 🥚 Eggs
* 💰 Silver
* ⚙️ Producción por hora

---

### 2. Conversión de recursos

* 100 huevos = 1 silver

El bot vende huevos automáticamente cada intervalo aleatorio:

```
1 a 20 segundos
```

---

### 3. Sistema de compra inteligente

El bot calcula:

* Recursos efectivos: `silver + eggs/100`
* Producción por segundo
* Tiempo necesario para cada ave

Luego decide:

* ✅ Mejor ave comprable en ≤ 1 hora
* 🧠 Fallback: la más cercana si todas tardan mucho

---

### 4. Compra automática

* Compra en cuanto puede
* Prioriza crecimiento continuo
* Evita esperar acumulaciones grandes

---

## 📊 Dashboard

La consola muestra:

* Recursos actuales
* Producción
* Mejor ave objetivo
* ETA (tiempo estimado)
* Tiempo para próxima venta

---

## ⚠️ Problemas comunes

### ❌ Error ChromeDriver

```
session not created: This version of ChromeDriver only supports Chrome version X
```

### ✅ Solución

En `Login.py`:

```
uc.Chrome(version_main=TU_VERSION)
```

---

## 💡 Sugerencias de mejora

### 🔥 1. Estrategia avanzada de compra

Actualmente:

* Compra basado en costo

Mejorable a:

* ROI (retorno por inversión)
* Payback time

---

### ⚡ 2. Eliminar Selenium

* Extraer token directamente (más rápido)
* Evitar errores de Chrome

---

### 📈 3. Sistema de optimización

* Simulación predictiva
* Compra óptima por etapas

---

### 🧾 4. Logging

* Guardar historial en archivo
* Estadísticas de crecimiento

---

### 🤖 5. Multi-cuenta

* Ejecutar múltiples bots simultáneamente

---

## 🧠 Conceptos clave

* Snowball growth (crecimiento acumulativo)
* Optimización de recursos en tiempo real
* Automatización basada en eventos

---

## 🚀 Ejecución

```
python bot.py
```

---

## ⚠️ Disclaimer

Este bot es solo para fines educativos.
El uso puede violar términos del juego.

---

## 👤 Autor

Desarrollado para automatización y optimización de juegos Web3/Telegram.
