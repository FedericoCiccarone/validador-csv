# 🧾 Validador CSV - Nubceo

Aplicación inteligente para validar, normalizar y preparar archivos CSV de ventas antes de cargarlos en Nubceo.

---

# 🚀 Funcionalidades

## ✅ Validación estructural
- Validación de columnas obligatorias
- Validación de columnas esperadas
- Detección de columnas faltantes
- Mapeo inteligente de columnas

---

# ✅ Validaciones de negocio
- Validación de montos
- Validación de fechas
- Validación de tipos de pago
- Validación de marcas de tarjeta
- Validación de platform codes
- Validación contable
- Validación de pagos múltiples

---

# 🧠 Smart Fix Inteligente
La aplicación detecta errores y permite:

- Corregir valores inválidos
- Aplicar correcciones masivas
- Aprender sugerencias anteriores
- Reutilizar sugerencias futuras

Actualmente soporta:
- Tipo de pago
- Marca de tarjeta
- Correcciones contables

---

# 🧮 Smart Fix Contable
La aplicación detecta automáticamente:

- Neto = Bruto
- Impuestos vacío

Y sugiere:
```text
Impuestos = 0

---

# 🚀 Instalación

## 1️⃣ Descargar el proyecto

Descargar el ZIP desde GitHub y descomprimirlo.

---

## 2️⃣ Ejecutar instalación

Hacer doble click en:

```bash
instalar.bat

Esto instalará automáticamente todas las librerías necesarias.

3️⃣ Iniciar aplicación

Hacer doble click en:

iniciar.bat

La aplicación abrirá automáticamente en el navegador.

📂 Formato esperado
CSV
Separador ;
UTF-8

⚠️ La aplicación detecta archivos Latin-1 e informa al usuario.

🛠️ Tecnologías utilizadas
Python
Pandas
Streamlit
OpenPyXL

👨‍💻 Autor
Federico Ciccarone
