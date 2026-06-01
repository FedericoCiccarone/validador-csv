import sys
import os
import time
import difflib
import csv
from io import StringIO


# =============================
# 🔎 VALIDAR ESTRUCTURA CSV
# =============================

def validar_estructura_csv(archivo):

    errores = []

    archivo.seek(0)

    contenido = archivo.getvalue().decode(
        "utf-8",
        errors="ignore"
    )

    lector = csv.reader(
        StringIO(contenido),
        delimiter=";"
    )

    filas = list(lector)

    if not filas:
        archivo.seek(0)
        return errores

    columnas_esperadas = len(filas[0])

    for numero, fila in enumerate(
        filas[1:],
        start=2
    ):

        columnas_actuales = len(fila)

        if columnas_actuales != columnas_esperadas:

            errores.append({
                "fila": numero,
                "detalle_error":
                    (
                        "Estructura CSV inválida; "
                        f"se esperaban {columnas_esperadas} columnas "
                        f"y se encontraron {columnas_actuales}"
                    )
            })

    archivo.seek(0)

    return errores


# 👇 IMPORTANTE PARA PORTABLE

sys.path.append(
    os.path.join(
        os.path.dirname(__file__),
        "libs"
    )
)
import streamlit as st
import pandas as pd
from io import BytesIO
import pandas as pd
from io import BytesIO

from validator import validar_archivo
from rules import sugerir_reglas

from smart_fix import (
    detectar_valores_invalidos,
    aplicar_correccion,
    guardar_sugerencia,
    obtener_sugerencia
)

from config import (
    COLUMNAS_OBLIGATORIAS,
    COLUMNAS_ESPERADAS,
    TIPOS_PAGO_VALIDOS,
    CARD_BRANDS_VALIDOS,
    PLATFORM_CODES_VALIDOS
)

st.title("🧾 Validador de Ventas - Nubceo")

st.info(
    "ℹ️ Nubceo solo acepta archivos CSV separados por ';' y en formato UTF-8"
)

archivo = st.file_uploader(
    "Subí tu archivo CSV",
    type=["csv"]
)

# =============================
# 📂 CARGA ARCHIVO
# =============================

if archivo:

    # =============================
    # 🧹 LIMPIAR ERRORES ANTERIORES
    # =============================

    if "error_estructura_csv" in st.session_state:

        del st.session_state[
            "error_estructura_csv"
        ]



    if not archivo.name.endswith(".csv"):

        st.error(
            "❌ Formato inválido. Solo se permiten archivos .CSV"
        )

        st.stop()

    size_mb = archivo.size / (1024 * 1024)

    # =============================
    # 🔎 VALIDAR ESTRUCTURA CSV
    # =============================

    errores_csv = validar_estructura_csv(
        archivo
    )


    try:

        try:

            df = pd.read_csv(
                archivo,
                sep=";",
                encoding="utf-8",
                engine="python",
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip"

            )

        except UnicodeDecodeError:

            archivo.seek(0)

            df = pd.read_csv(
                archivo,
                sep=";",
                encoding="latin-1",
                engine="python",
                quoting=csv.QUOTE_NONE,
                on_bad_lines="skip"
            )

            st.warning(
                "⚠️ El archivo está en Latin-1"
            )

        if df.empty:

            st.error("❌ Archivo vacío")

            st.stop()

    except Exception as e:

        st.error(
            "❌ No se pudo leer el CSV"
        )

        st.error(
            str(e)
        )

        st.stop()
    # =============================
    # 🧹 LIMPIEZA COLUMNAS
    # =============================

    df.columns = (
        df.columns
        .astype(str)
        .str.replace(
            '"',
            "",
            regex=False
        )
        .str.strip()
    )


    for col in df.columns:

        if df[col].dtype == "object":

            df[col] = (
                df[col]
                .astype(str)

                # 🔥 eliminar cualquier cantidad de comillas
                .str.replace(
                    '"',
                    "",
                    regex=False
                )

                # 🔥 limpiar espacios
                .str.strip()
            )


            # 🔥 corregir campos que quedaron como comillas vacías
            df[col] = (
                df[col]
                .replace(
                    [
                        "",
                        "nan",
                        "NaN",
                        "None"
                    ],
                    ""
                )
            )


    # 🔥 eliminar columnas basura tipo Unnamed
    df = df.loc[
        :,
        ~df.columns.str.contains("^Unnamed")
    ]

    # =============================
    # 🧹 LIMPIEZA REAL CSV
    # =============================
    df.columns = [
        str(col)
        .replace('"', '')
        .strip()

        for col in df.columns
    ]


    for columna in df.columns:

        df[columna] = (
            df[columna]
            .astype(str)
            .str.replace(
                '"',
                '',
                regex=False
            )
            .str.strip()
        )

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

                default_index = opciones.index(
                    sugerencia[0]
                )

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

                    st.session_state[
                        "columnas_crear"
                    ] = []

                if (
                    col_faltante
                    not in st.session_state[
                        "columnas_crear"
                    ]
                ):

                    st.session_state[
                        "columnas_crear"
                    ].append(
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
            df = df.loc[
                :,
                ~df.columns.duplicated()
            ]

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
                columnas_layout +
                otras_columnas
            ]

            st.session_state[
                "df_mapeado"
            ] = df

            st.session_state[
                "mapeo_actual"
            ] = mapeo

            # 🔥 GUARDAR PERFIL
            if nombre_perfil:

                perfiles_dir = "perfiles"

                if not os.path.exists(
                    perfiles_dir
                ):

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

            st.success(
                "✅ Columnas mapeadas correctamente"
            )

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

                df = df.rename(
                    columns=mapeo_cargado
                )

                # 🔥 eliminar columnas duplicadas
                df = df.loc[
                    :,
                    ~df.columns.duplicated()
                ]

                st.session_state[
                    "df_mapeado"
                ] = df

                st.success(
                    f"✅ Perfil '{perfil_seleccionado}' aplicado"
                )

    # =============================
    # 📌 USAR DF MAPEADO
    # =============================

    if "df_mapeado" in st.session_state:

        df = st.session_state[
            "df_mapeado"
        ]

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

        with st.spinner(
            "🔄 Validando archivo..."
        ):

            if size_mb > 50:

                st.warning(
                    f"⚠️ Archivo grande ({round(size_mb,2)} MB). Procesando..."
                )

                archivo.seek(0)

                chunks = pd.read_csv(
                    archivo,
                    sep=";",
                    encoding="utf-8",
                    engine="python",
                    quoting=csv.QUOTE_NONE,
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
                    quoting=csv.QUOTE_NONE,
                    chunksize=50000,
                    on_bad_lines="skip"
                )

                for i, chunk in enumerate(
                    chunks,
                    start=1
                ):

                    chunk.columns = (
                        chunk.columns
                        .astype(str)
                        .str.strip()
                    )

                    # 🔥 limpiar columnas basura
                    chunk = chunk.loc[
                        :,
                        ~chunk.columns.str.contains(
                            "^Unnamed"
                        )
                    ]

                    if mapeo:

                        chunk = chunk.rename(
                            columns=mapeo
                        )

                    # 🔥 eliminar duplicadas
                    chunk = chunk.loc[
                        :,
                        ~chunk.columns.duplicated()
                    ]

                    df_val, _, _ = validar_archivo(
                        chunk
                    )

                    resultados.append(df_val)

                    progress.progress(i / total)

                df_validado = pd.concat(
                    resultados,
                    ignore_index=True
                )

                errores, warnings = [], []

            else:

                # =============================
                # 🧹 LIMPIEZA FINAL CSV
                # =============================
                for col in df.columns:

                    if df[col].dtype == "object":

                        df[col] = (
                            df[col]
                            .map(
                                lambda x:
                                str(x)
                                .replace(
                                    '"',
                                    ''
                                )
                                .strip()
                                if pd.notna(x)
                                else x
                            )
                        )


                df.columns = (
                    df.columns
                    .astype(str)
                    .str.replace(
                        '"',
                        '',
                        regex=False
                    )
                    .str.strip()
                )



                df.columns = (
                    df.columns
                    .astype(str)
                    .str.replace(
                        '"',
                        '',
                        regex=False
                    )
                    .str.strip()
                )


                df_validado, errores, warnings = validar_archivo(
                    df
                )




        st.success(
            f"✅ Validación completada en {round(time.time() - start, 2)} segundos"
        )

        st.session_state[
            "df_validado"
        ] = df_validado

        st.session_state[
            "errores"
        ] = errores

        st.session_state[
            "warnings"
        ] = warnings

# =============================
# 📊 RESULTADOS
# =============================

if "df_validado" in st.session_state:

    df_validado = st.session_state[
        "df_validado"
    ]

    errores = st.session_state[
        "errores"
    ]

    warnings = st.session_state[
        "warnings"
    ]

    if errores:

        st.error(
            "❌ Errores estructurales:"
        )

        for e in errores:

            st.write(f"- {e}")

    else:

        if warnings:

            with st.expander(
                "⚠️ Ver advertencias"
            ):

                for w in warnings:

                    st.write(f"- {w}")

        st.subheader("📊 Resultado (muestra)")

        # =============================
        # 🔥 PRIORIZAR ERRORES EN MUESTRA
        # =============================

        df_muestra = (
            df_validado
            .copy()
        )

        if "estado" in df_muestra.columns:

            df_muestra["_orden_error"] = (
                df_muestra["estado"]
                .apply(
                    lambda x: 0
                    if x == "ERROR"
                    else 1
                )
            )

            df_muestra = (
                df_muestra
                .sort_values(
                    "_orden_error"
                )
                .drop(
                    columns=[
                        "_orden_error"
                    ]
                )
            )

        st.dataframe(
            df_muestra.head(500)
        )


        st.subheader("📊 Resumen")

        # =============================
        # 🧾 CANTIDAD DE VENTAS
        # =============================

        if "ID de venta" in df_validado.columns:

            ventas = (
                df_validado["ID de venta"]
                .dropna()
                .astype(str)
                .str.strip()
            )

            ventas = (
                ventas[
                    ventas != ""
                ]
                .nunique()
            )

        else:

            ventas = 0


        # =============================
        # ✅ FILAS CSV OK
        # =============================

        filas_ok = (
            df_validado["estado"] == "OK"
        ).sum()


        # =============================
        # ❌ ERRORES
        # =============================

        error = (
            df_validado["estado"] == "ERROR"
        ).sum()


        # =============================
        # 💰 PROMEDIO VENTA
        # =============================

        df_validado[
            "Monto bruto venta"
        ] = pd.to_numeric(
            df_validado[
                "Monto bruto venta"
            ],
            errors="coerce"
        )


        promedio = (
            df_validado[
                "Monto bruto venta"
            ]
            .mean()
        )


        col1, col2, col3, col4 = st.columns(4)


        col1.metric(
            "🧾 Ventas",
            ventas
        )


        col2.metric(
            "📄 Filas CSV OK",
            filas_ok
        )


        col3.metric(
            "❌ Error",
            error
        )


        col4.metric(
            "📈 Promedio",
            f"${promedio:,.2f}"
        )

        # =============================
        # 🧠 SMART FIX
        # =============================

        st.subheader(
            "🧠 Correcciones inteligentes"
        )

        # =============================
        # 💳 TIPOS DE PAGO
        # =============================

        invalidos_pago = detectar_valores_invalidos(
            df_validado,
            "Tipo de pago",
            set(
                x.upper().strip()
                 for x in TIPOS_PAGO_VALIDOS
            )
        )

        for i, invalido in enumerate(
            invalidos_pago
        ):

            st.warning(
                f"⚠️ Valor inválido detectado en 'Tipo de pago': {invalido}"
            )

            sugerencia = obtener_sugerencia(
                "Tipo de pago",
                invalido
            )

            if sugerencia:

                st.info(
                    f"🧠 Sugerencia aprendida: {sugerencia}"
                )

            nuevo_valor = st.text_input(
                f"Nuevo valor para '{invalido}'",
                value=sugerencia if sugerencia else "",
                key=f"smartfix_pago_{i}"
            )

            aplicar_masivo = st.checkbox(
                f"Aplicar a todos los '{invalido}'",
                value=True,
                key=f"masivo_pago_{i}"
            )

            if st.button(
                f"✅ Corregir '{invalido}'",
                key=f"btn_pago_{i}"
            ):

                df_validado = aplicar_correccion(
                    df_validado,
                    "Tipo de pago",
                    invalido,
                    nuevo_valor,
                    aplicar_masivo
                )

                guardar_sugerencia(
                    "Tipo de pago",
                    invalido,
                    nuevo_valor
                )

                st.session_state[
                    "df_validado"
                ] = df_validado

                st.success(
                    f"✅ Corrección aplicada: {invalido} → {nuevo_valor}"
                )

        # =============================
        # 🧠 SMART FIX PLATFORM CODE
        # =============================

        invalidos_platform = detectar_valores_invalidos(
            df_validado,
            "Codigo Plataforma Externa",
            PLATFORM_CODES_VALIDOS
        )

        for i, invalido in enumerate(
            invalidos_platform
        ):

            st.warning(
                f"⚠️ Platform code inválido detectado: {invalido}"
            )

            sugerencia = obtener_sugerencia(
                "Codigo Plataforma Externa",
                invalido
            )

            opciones_platform = [
                "",
            ] + PLATFORM_CODES_VALIDOS

            default_index = 0

            if (
                sugerencia
                and sugerencia in opciones_platform
            ):

                default_index = (
                    opciones_platform.index(
                        sugerencia
                    )
                )

            nuevo_valor = st.selectbox(
                f"Nuevo valor para '{invalido}'",
                opciones_platform,
                index=default_index,
                key=f"smartfix_platform_{i}"
            )

            aplicar_masivo = st.checkbox(
                f"Aplicar a todos los '{invalido}'",
                value=True,
                key=f"masivo_platform_{i}"
            )

            if st.button(
                f"✅ Corregir platform '{invalido}'",
                key=f"btn_platform_{i}"
            ):

                df_validado = aplicar_correccion(
                    df_validado,
                    "Codigo Plataforma Externa",
                    invalido,
                    nuevo_valor,
                    aplicar_masivo
                )

                guardar_sugerencia(
                    "Codigo Plataforma Externa",
                    invalido,
                    nuevo_valor
                )

                st.session_state[
                    "df_validado"
                ] = df_validado

                st.success(
                    f"✅ Corrección aplicada: {invalido} → {nuevo_valor}"
                )

        # =============================
        # 💳 MARCAS TARJETA
        # =============================

        invalidos_brand = detectar_valores_invalidos(
            df_validado,
            "Marca de tarjeta",
            set(
                 x.upper().strip()
                 for x in CARD_BRANDS_VALIDOS
            )
        )

        for i, invalido in enumerate(
            invalidos_brand
        ):

            st.warning(
                f"⚠️ Valor inválido detectado en 'Marca de tarjeta': {invalido}"
            )

            sugerencia = obtener_sugerencia(
                "Marca de tarjeta",
                invalido
            )

            if sugerencia:

                st.info(
                    f"🧠 Sugerencia aprendida: {sugerencia}"
                )

            nuevo_valor = st.text_input(
                f"Nuevo valor para marca '{invalido}'",
                value=sugerencia if sugerencia else "",
                key=f"smartfix_brand_{i}"
            )

            aplicar_masivo = st.checkbox(
                f"Aplicar a todas las '{invalido}'",
                value=True,
                key=f"masivo_brand_{i}"
            )

            if st.button(
                f"✅ Corregir marca '{invalido}'",
                key=f"btn_brand_{i}"
            ):

                df_validado = aplicar_correccion(
                    df_validado,
                    "Marca de tarjeta",
                    invalido,
                    nuevo_valor,
                    aplicar_masivo
                )

                guardar_sugerencia(
                    "Marca de tarjeta",
                    invalido,
                    nuevo_valor
                )

                st.session_state[
                    "df_validado"
                ] = df_validado

                st.success(
                    f"✅ Corrección aplicada: {invalido} → {nuevo_valor}"
                )
        # =============================
        # 🧮 SMART FIX CONTABLE
        # =============================

        st.subheader(
            "🧮 Correcciones contables"
        )

        if all(col in df_validado.columns for col in [
            "Monto neto",
            "Monto bruto venta",
            "Impuestos"
        ]):

            neto = pd.to_numeric(
                df_validado["Monto neto"],
                errors="coerce"
            )

            bruto = pd.to_numeric(
                df_validado["Monto bruto venta"],
                errors="coerce"
            )

            impuestos_raw = df_validado["Impuestos"]

            impuestos = (
                impuestos_raw
                .fillna("")
                .astype(str)
                .str.strip()
                .str.upper()
            )

            # 🔥 detectar:
            # neto == bruto
            # impuestos vacío

            mask_impuestos_vacio = (
                (neto == bruto) &
                (
                    impuestos.isin([
                        "",
                        "nan",
                        "None",
                        "<NA>"
                    ])
                )
            )

            cantidad = mask_impuestos_vacio.sum()

            if cantidad > 0:

                st.warning(
                    f"⚠️ Se detectaron {cantidad} registros donde Impuestos está vacío y Neto = Bruto"
                )

                st.info(
                    "💡 Se sugiere completar Impuestos = 0"
                )

                aplicar_correccion_impuestos = st.checkbox(
                    "Aplicar Impuestos = 0",
                    value=True,
                    key="fix_impuestos"
                )

                if st.button(
                    "✅ Aplicar corrección contable"
                ):

                    if aplicar_correccion_impuestos:

                        df_validado.loc[
                            mask_impuestos_vacio,
                            "Impuestos"
                        ] = 0

                        st.session_state[
                            "df_validado"
                        ] = df_validado

                        st.success(
                            "✅ Corrección aplicada"
                        )


        # =============================
        # 🧠 REGLAS SUGERIDAS
        # =============================

        st.subheader("🧠 Reglas sugeridas")

        reglas = sugerir_reglas(
            df_validado
        )

        for tipo in [
            "estricta",
            "intermedia",
            "flexible"
        ]:

            st.write(
                f"### {tipo.upper()}"
            )

            r = reglas[tipo]

            if r["ok"]:

                st.success(
                    "Aplicable"
                )

                for c in r["campos"]:

                    st.write(f"- {c}")

                st.write(
                    r["tolerancia"]
                )

            else:

                st.error(
                    r.get(
                        "motivo",
                        "No aplicable"
                    )
                )

        # =============================
        # 📤 EXPORTAR CSV NUBCEO
        # =============================


        layout_nubceo = [
        "ID de venta",
        "CUIT",
        "Sucursal",
        "Fecha",
        "Moneda venta",
        "Tipo",
        "Monto bruto venta",
        "Monto neto",
        "Impuestos",
        "Categoria",
        "Sub categoria",
        "Sub categoria 2",
        "Codigo de referencia",
        "ID de pago",
        "Codigo Plataforma Externa",
        "Fecha del pago",
        "Fecha de presentacion",
        "Lote",
        "Voucher",
        "Terminal",
        "Codigo de autorizacion",
        "Referencia de sucursal de plataforma",
        "Monto bruto pago",
        "Marca de tarjeta",
        "Numero de tarjeta",
        "Numero de identificacion del cliente",
        "Cuotas",
        "Codigo de promocion",  
        "Tipo de pago",
        "Referencia externa",
        "Comodin 1",
        "Comodin 2",
        "Moneda pago",
        "Tasa de conversion",
        "Importe convertido"
        ]

        # 🔥 usar solo columnas Nubceo
        columnas_exportar = [
            c for c in layout_nubceo
            if c in df_validado.columns
        ]
        df_exportar = df_validado[
            columnas_exportar
        ].copy()

        # 🔥 reordenar EXACTAMENTE
        df_exportar = df_exportar.reindex(
            columns=layout_nubceo
        )

        # 🔥 eliminar columnas internas
        for col in ["estado", "detalle_error"]:
            if col in df_exportar.columns:

                df_exportar = df_exportar.drop(
                         columns=[col]
        )

        # =============================
        # 📤 EXPORTAR EXCEL
        # =============================



        output = BytesIO()

        with pd.ExcelWriter(
            output,
            engine="openpyxl"
        ) as writer:

            df_exportar.to_excel(
                writer,
                index=False,
                sheet_name="Nubceo"
            )

            errores_df = df_validado[
                df_validado["estado"] == "ERROR"
            ]

            errores_df.to_excel(
                writer,
                index=False,
                sheet_name="Errores"
            )

        st.markdown("---")
        st.subheader("📥 Barra de descargas")

        col_xlsx, col_csv = st.columns(2)

        col_xlsx.download_button(
            "📥 Descargar Excel",
            output.getvalue(),
            "resultado_validado.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        # =============================
        # 📤 EXPORTAR CSV NUBCEO
        # =============================

        csv = df_exportar.to_csv(
            sep=";",
            index=False,
            encoding="utf-8-sig"
        )

        col_csv.download_button(
            "📤 Descargar CSV Nubceo",
             csv,
             "nubceo_import.csv",
             "text/csv"
        )

        st.info(
            "Si no ves los botones, baja hasta esta barra de descargas o recarga la página para forzar el renderizado."
        )