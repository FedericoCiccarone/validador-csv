import sys
import os
import time

# 👇 IMPORTANTE PARA PORTABLE
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import streamlit as st
import pandas as pd
from io import BytesIO
from validator import validar_archivo
from rules import sugerir_reglas

st.title("🧾 Validador de Ventas - Nubceo")

st.info("ℹ️ Nubceo solo acepta archivos CSV separados por ';' y en formato UTF-8")

archivo = st.file_uploader("Subí tu archivo CSV", type=["csv"])

if archivo:
    if not archivo.name.endswith(".csv"):
        st.error("❌ Formato inválido. Solo se permiten archivos .CSV")
        st.stop()

    size_mb = archivo.size / (1024 * 1024)

    try:
        try:
            df = pd.read_csv(
                archivo,
                sep=";",
                encoding="utf-8"
            )
        except UnicodeDecodeError:
            archivo.seek(0)

            df = pd.read_csv(
                archivo,
                sep=";",
                encoding="latin-1",
                engine="python",
                on_bad_lines="skip"
            )

            st.error("❌ El archivo no está en UTF-8")
            st.warning("⚠️ Está en Latin-1. Convertir antes de subir a Nubceo")

        if df.empty:
            st.error("❌ Archivo vacío")
            st.stop()

    except Exception as e:
        st.error("❌ Error al leer archivo")
        st.code(str(e))
        st.stop()

    st.subheader("📄 Vista previa")
    st.dataframe(df.head())

    if st.button("Validar archivo"):

        start = time.time()

        with st.spinner("🔄 Validando archivo, esto puede tardar unos segundos..."):

            if size_mb > 50:
                st.warning(f"⚠️ Archivo grande ({round(size_mb,2)} MB). Procesando en partes...")

                archivo.seek(0)

                chunks = pd.read_csv(
                    archivo,
                    sep=";",
                    encoding="latin-1",
                    engine="python",
                    chunksize=50000,
                    on_bad_lines="skip"
                )

                resultados = []
                progress = st.progress(0)

                total = sum(1 for _ in chunks)

                archivo.seek(0)

                chunks = pd.read_csv(
                    archivo,
                    sep=";",
                    encoding="latin-1",
                    engine="python",
                    chunksize=50000,
                    on_bad_lines="skip"
                )

                for i, chunk in enumerate(chunks, start=1):
                    df_val, _, _ = validar_archivo(chunk)
                    resultados.append(df_val)

                    progress.progress(i / total)

                df_validado = pd.concat(resultados, ignore_index=True)
                errores, warnings = [], []

            else:
                df_validado, errores, warnings = validar_archivo(df)

        st.success(f"✅ Validación completada en {round(time.time() - start, 2)} segundos")

        st.session_state["df_validado"] = df_validado
        st.session_state["errores"] = errores
        st.session_state["warnings"] = warnings


# =============================
# 📊 RESULTADOS
# =============================

if "df_validado" in st.session_state:

    df_validado = st.session_state["df_validado"]
    errores = st.session_state["errores"]
    warnings = st.session_state["warnings"]

    if errores:
        st.error("❌ Errores estructurales:")
        for e in errores:
            st.write(f"- {e}")
    else:
        if warnings:
            st.warning("⚠️ Advertencias:")
            for w in warnings:
                st.write(f"- {w}")

        st.subheader("📊 Resultado (muestra)")
        st.dataframe(df_validado.head(500))

        st.subheader("📊 Resumen")

        df_validado["Monto bruto venta"] = pd.to_numeric(
            df_validado["Monto bruto venta"], errors="coerce"
        )

        ok = (df_validado["estado"] == "OK").sum()
        error = (df_validado["estado"] == "ERROR").sum()
        promedio = df_validado["Monto bruto venta"].mean()

        col1, col2, col3 = st.columns(3)
        col1.metric("✅ OK", ok)
        col2.metric("❌ Error", error)
        col3.metric("📈 Promedio", f"${promedio:,.2f}")

        st.subheader("🧠 Reglas sugeridas")
        reglas = sugerir_reglas(df_validado)

        for tipo in ["estricta", "intermedia", "flexible"]:
            st.write(f"### {tipo.upper()}")
            r = reglas[tipo]

            if r["ok"]:
                st.success("Aplicable")
                for c in r["campos"]:
                    st.write(f"- {c}")
                st.write(r["tolerancia"])
            else:
                st.error(r.get("motivo", "No aplicable"))

        # 📥 EXCEL
        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_validado.to_excel(writer, index=False, sheet_name="Completo")

            errores_df = df_validado[df_validado["estado"] == "ERROR"]
            errores_df.to_excel(writer, index=False, sheet_name="Errores")

        st.download_button(
            "📥 Descargar Excel",
            output.getvalue(),
            "resultado_validado.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )