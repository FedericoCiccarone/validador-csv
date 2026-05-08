# 🧾 Validador CSV - Nubceo

Aplicación para validar, corregir y normalizar archivos CSV de ventas antes de cargarlos en Nubceo.

---

# ✅ Funcionalidades

## 🔎 Validaciones automáticas

- Validación estructural de archivos CSV
- Validación de:
  - montos
  - fechas
  - tipos de pago
  - marcas de tarjeta
  - platform codes
- Validación contable:
  - Neto + Impuestos = Bruto
- Validación de pagos múltiples por venta
- Validación de IDs de pago duplicados
- Detección de inconsistencias

---

# 🧠 Funcionalidades inteligentes

- Mapeo inteligente de columnas
- Auto sugerencia de columnas similares
- Creación automática de columnas faltantes
- Reordenamiento automático de layout Nubceo
- Eliminación automática de columnas basura (`Unnamed`)
- Normalización automática de layouts

---

# ✏️ Corrección integrada

- Corrección manual dentro de la app
- Revalidación automática
- Exportación de CSV corregido listo para Nubceo

---

# 📂 Perfiles de importación

- Guardado de perfiles reutilizables
- Aplicación automática de mapeos frecuentes

---

# 📊 Resultados y reportes

- Exportación a Excel
- Hoja completa
- Hoja de errores
- Resumen de validación
- Sugerencia automática de reglas de conciliación

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
