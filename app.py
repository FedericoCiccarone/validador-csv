import sys
import os
import time
import difflib

# 👇 IMPORTANTE PARA PORTABLE
sys.path.append(os.path.join(os.path.dirname(__file__), "libs"))

import streamlit as st
import pandas as pd
from io import BytesIO
from validator import validar_archivo
from rules import sugerir_reglas

from config import (
    COLUMNAS_OBLIGATORIAS,
    COLUMNAS_ESPERADAS
)

st.title("🧾 Validador de Ventas - Nubceo")

st.info("ℹ️ Nubceo solo acepta archivos CSV separados por ';' y en formato UTF-8")

archivo = st.file_uploader("Subí tu archivo CSV", type=["csv"])

# =============================
# 📂 CARGA ARCHIVO
# =============================

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

            st.warning("⚠️ El archivo está en Latin-1")

        if df.empty:
            st.error("❌ Archivo vacío")
            st.stop()

    except Exception as e:

        st.error("❌ Error al leer archivo")
        st.code(str(e))
        st.stop()

    # =============================
    # 🧹 LIMPIEZA COLUMNAS
    # =============================

    df.columns = df.columns.astype(str).str.strip()

    # 🔥 eliminar columnas basura tipo Unnamed
    df = df.loc[
        :,
        ~df.columns.str.contains("^Unnamed")
    ]

    st.subheader("📄 Vista previa")
    st.dataframe(df.head())

    # =============================
    # 🔎 DETECTAR COLUMNAS FALTANTES
    # =============================

    todas_columnas = (
        COLUMNAS_OBLIGATORIAS +
        COLUMNAS_ESPERADAS
    )

    columnas_faltantes = [
        col for col in todas_columnas
        if col not in df.columns
    ]

    mapeo = {}

    # =============================
    # 🧠 MAPEADOR INTELIGENTE
    # =============================

    if columnas_faltantes:

        st.warning(
            "⚠️ Faltan columnas requeridas para Nubceo"
        )

        st.subheader("🛠️ Mapear columnas")

        for i, col_faltante in enumerate(columnas_faltantes):

            sugerencia = difflib.get_close_matches(
                col_faltante,
                df.columns,
                n=1,
                cutoff=0.4
            )

            columnas_visibles = list(df.columns)

            opciones = [
                "-- No existe --",
                "➕ Crear columna vacía"
            ] + columnas_visibles

            default_index = 0

            if sugerencia and sugerencia[0] in opciones:
                default_index = opciones.index(sugerencia[0])

            opcion = st.selectbox(
                f"Columna para: '{col_faltante}'",
                opciones,
                index=default_index,
                key=f"map_{col_faltante}_{i}"
            )

            if opcion not in [
                "-- No existe --",
                "➕ Crear columna vacía"
            ]:
                mapeo[opcion] = col_faltante

            # 🔥 marcar columnas a crear
            if opcion == "➕ Crear columna vacía":

                if "columnas_crear" not in st.session_state:
                    st.session_state["columnas_crear"] = []

                if col_faltante not in st.session_state["columnas_crear"]:

                    st.session_state["columnas_crear"].append(
                        col_faltante
                    )

        # =============================
        # 💾 GUARDAR PERFIL
        # =============================

        st.caption(
            "⚠️ El nombre del perfil no puede contener estos caracteres: \\ / : * ? \" < > |"
        )

        nombre_perfil = st.text_input(
            "💾 Nombre del perfil de importación",
            placeholder="Ej: Northville_Abril"
        )

        if st.button("✅ Aplicar mapeo"):

            # 🔥 RENOMBRAR COLUMNAS
            df = df.rename(columns=mapeo)

            # 🔥 eliminar columnas duplicadas
            df = df.loc[:, ~df.columns.duplicated()]

            # =============================
            # ➕ CREAR COLUMNAS FALTANTES
            # =============================

            columnas_crear = st.session_state.get(
                "columnas_crear",
                []
            )

            for col in columnas_crear:

                if col not in df.columns:
                    df[col] = ""

            # =============================
            # 🔥 REORDENAR COLUMNAS
            # =============================

            layout_nubceo = (
                COLUMNAS_OBLIGATORIAS +
                COLUMNAS_ESPERADAS
            )

            columnas_layout = [
                c for c in layout_nubceo
                if c in df.columns
            ]

            otras_columnas = [
                c for c in df.columns
                if c not in columnas_layout
            ]

            df = df[
                columnas_layout + otras_columnas
            ]

            st.session_state["df_mapeado"] = df
            st.session_state["mapeo_actual"] = mapeo

            # 🔥 GUARDAR PERFIL
            if nombre_perfil:

                perfiles_dir = "perfiles"

                if not os.path.exists(perfiles_dir):
                    os.makedirs(perfiles_dir)

                perfil_path = os.path.join(
                    perfiles_dir,
                    f"{nombre_perfil}.json"
                )

                pd.Series(mapeo).to_json(
                    perfil_path,
                    force_ascii=False,
                    indent=4
                )

                st.success(
                    f"✅ Perfil '{nombre_perfil}' guardado"
                )

            st.success("✅ Columnas mapeadas correctamente")

            # =============================
            # 📋 MOSTRAR COLUMNAS CREADAS
            # =============================

            if columnas_crear:

                st.info(
                    "➕ Columnas creadas automáticamente:"
                )

                for c in columnas_crear:
                    st.write(f"- {c}")

    # =============================
    # 📂 CARGAR PERFIL
    # =============================

    perfiles_dir = "perfiles"

    if os.path.exists(perfiles_dir):

        perfiles = [
            f.replace(".json", "")
            for f in os.listdir(perfiles_dir)
            if f.endswith(".json")
        ]

        if perfiles:

            st.subheader("📂 Cargar perfil")

            perfil_seleccionado = st.selectbox(
                "Seleccioná un perfil",
                ["-- Ninguno --"] + perfiles
            )

            if (
                perfil_seleccionado != "-- Ninguno --"
                and st.button("📥 Aplicar perfil")
            ):

                perfil_path = os.path.join(
                    perfiles_dir,
                    f"{perfil_seleccionado}.json"
                )

                mapeo_cargado = pd.read_json(
                    perfil_path,
                    typ="series"
                ).to_dict()

                df = df.rename(columns=mapeo_cargado)

                # 🔥 eliminar columnas duplicadas
                df = df.loc[:, ~df.columns.duplicated()]

                st.session_state["df_mapeado"] = df

                st.success(
                    f"✅ Perfil '{perfil_seleccionado}' aplicado"
                )

    # =============================
    # 📌 USAR DF MAPEADO
    # =============================

    if "df_mapeado" in st.session_state:
        df = st.session_state["df_mapeado"]

    # =============================
    # 🔎 VALIDAR OBLIGATORIAS
    # =============================

    faltantes_finales = [
        col for col in COLUMNAS_OBLIGATORIAS
        if col not in df.columns
    ]

    if faltantes_finales:

        st.error(
            "❌ Todavía faltan columnas obligatorias:"
        )

        for col in faltantes_finales:
            st.write(f"- {col}")

        st.stop()

    # =============================
    # ✅ VALIDAR
    # =============================

    if st.button("Validar archivo"):

        start = time.time()

        with st.spinner("🔄 Validando archivo..."):

            if size_mb > 50:

                st.warning(
                    f"⚠️ Archivo grande ({round(size_mb,2)} MB). Procesando..."
                )

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

                    chunk.columns = chunk.columns.astype(str).str.strip()

                    # 🔥 limpiar columnas basura también en chunks
                    chunk = chunk.loc[
                        :,
                        ~chunk.columns.str.contains("^Unnamed")
                    ]

                    if mapeo:
                        chunk = chunk.rename(columns=mapeo)

                    # 🔥 eliminar columnas duplicadas
                    chunk = chunk.loc[:, ~chunk.columns.duplicated()]

                    df_val, _, _ = validar_archivo(chunk)

                    resultados.append(df_val)

                    progress.progress(i / total)

                df_validado = pd.concat(resultados, ignore_index=True)

                errores, warnings = [], []

            else:

                df_validado, errores, warnings = validar_archivo(df)

        st.success(
            f"✅ Validación completada en {round(time.time() - start, 2)} segundos"
        )

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

            with st.expander("⚠️ Ver advertencias"):

                for w in warnings:
                    st.write(f"- {w}")

        st.subheader("📊 Resultado (muestra)")
        st.dataframe(df_validado.head(500))

        st.subheader("📊 Resumen")

        df_validado["Monto bruto venta"] = pd.to_numeric(
            df_validado["Monto bruto venta"],
            errors="coerce"
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

        # =============================
        # 📥 EXPORTAR EXCEL
        # =============================

        output = BytesIO()

        with pd.ExcelWriter(output, engine="openpyxl") as writer:

            df_validado.to_excel(
                writer,
                index=False,
                sheet_name="Completo"
            )

            errores_df = df_validado[
                df_validado["estado"] == "ERROR"
            ]

            errores_df.to_excel(
                writer,
                index=False,
                sheet_name="Errores"
            )

        st.download_button(
            "📥 Descargar Excel",
            output.getvalue(),
            "resultado_validado.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # =============================
        # ✏️ CORRECCIÓN MANUAL
        # =============================

        st.subheader("✏️ Corregir errores manualmente")

        errores_df = df_validado[
            df_validado["estado"] == "ERROR"
        ].copy()

        if not errores_df.empty:

            st.info(
                "Editá los valores y luego hacé click en 'Revalidar correcciones'"
            )

            columnas_prioridad = [
                "estado",
                "detalle_error"
            ] + COLUMNAS_OBLIGATORIAS

            columnas_existentes = [
                c for c in columnas_prioridad
                if c in errores_df.columns
            ]

            otras_columnas = [
                c for c in errores_df.columns
                if c not in columnas_existentes
            ]

            errores_df = errores_df[
                columnas_existentes + otras_columnas
            ]

            editable_df = st.data_editor(
                errores_df,
                use_container_width=True,
                num_rows="dynamic"
            )

            if st.button("🔄 Revalidar correcciones"):

                with st.spinner("Revalidando correcciones..."):

                    df_revalidado, errores2, warnings2 = validar_archivo(
                        editable_df
                    )

                    st.session_state["df_revalidado"] = df_revalidado

                st.success("✅ Correcciones revalidadas")

# =============================
# 📥 DESCARGA CORREGIDA
# =============================

if "df_revalidado" in st.session_state:

    df_revalidado = st.session_state["df_revalidado"]

    st.subheader("📄 Resultado corregido")

    st.dataframe(df_revalidado.head(500))

    csv = df_revalidado.to_csv(
        sep=";",
        index=False,
        encoding="utf-8-sig"
    )

    st.download_button(
        "📥 Descargar CSV corregido",
        csv,
        "archivo_corregido.csv",
        "text/csv"
    )