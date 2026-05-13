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
- Validación obligatoria de CUIT
- Validación exacta del campo Tipo
- Compatibilidad con reglas Nubceo
- Validación multipago avanzada
- 
---

# 🧠 Smart Fix Inteligente
La aplicación detecta errores y permite:

- Corregir valores inválidos
- Aplicar correcciones masivas
- Aprender sugerencias anteriores
- Reutilizar sugerencias futuras
- Eliminación de falsos positivos
- Normalización inteligente

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

Impuestos = 0

con confirmación del usuario.

📂 Perfiles de importación

Permite:

Guardar perfiles de mapeo
Reutilizar perfiles
Automatizar cargas repetitivas
📤 Exportador Nubceo

La aplicación exporta:

✅ CSV Nubceo
UTF-8
Separado por ;
Orden exacto requerido por Nubceo
Sin columnas internas
✅ Excel de validación
Resultado completo
Hoja de errores

```text
🚀 Instalación
1️⃣ Descargar proyecto

Descargar el ZIP desde GitHub y descomprimirlo.

2️⃣ Instalar dependencias

Ejecutar:

instalar.bat
3️⃣ Iniciar aplicación

Ejecutar:

iniciar.bat

La aplicación abrirá automáticamente en el navegador.

📂 Formato esperado
CSV
Separador ;
UTF-8
⚠️ Importante

La aplicación:

Detecta archivos Latin-1
Corrige estructuras inválidas
Permite crear columnas faltantes
Mantiene el layout oficial Nubceo
🛣️ Roadmap
Próximas mejoras
Smart Fix de fechas
Smart Fix de monedas
Reglas automáticas avanzadas
Publicación web
Integración directa con Nubceo
Historial de correcciones
Dashboard de validaciones
👨‍💻 Autor

Federico Ciccarone
