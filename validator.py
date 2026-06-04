import pandas as pd
from config import (
    COLUMNAS_OBLIGATORIAS,
    COLUMNAS_ESPERADAS,
    CARD_BRANDS_VALIDOS,
    PLATFORM_CODES_VALIDOS,
    TIPOS_PAGO_VALIDOS,
    TIPOS_DOCUMENTO_VALIDOS
)

# 🔥 NORMALIZADOR GLOBAL
def normalizar_texto(texto):

    if pd.isna(texto):
        return texto

    texto = str(texto)

    texto = texto.replace("\xa0", " ")

    texto = " ".join(texto.split())

    texto = texto.upper()

    return texto


def normalizar_lista(lista):

    return set(
        normalizar_texto(x)
        for x in lista
    )


def validar_archivo(df):

    errores = []
    warnings = []

    # =============================
    # 🔴 VALIDAR DATAFRAME
    # =============================

    if not isinstance(df, pd.DataFrame):

        return (
            None,
            ["El archivo no pudo ser procesado correctamente"],
            []
        )

    # =============================
    # 🧹 LIMPIEZA COLUMNAS
    # =============================

    df = df.copy()


    # 🔥 limpiar nombres columnas
    df.columns = (
        df.columns
        .astype(str)
        .str.replace(
            '"',
            "",
            regex=False
        )
        .str.replace(
            "\r",
            "",
            regex=False
        )
        .str.replace(
            "\n",
            "",
            regex=False
        )
        .str.strip()
    )


    # 🔥 eliminar columnas duplicadas
    df = df.loc[
        :,
        ~df.columns.duplicated()
    ]


    # 🔥 limpiar contenido de TODAS las celdas
    for col in df.columns:

        df[col] = (
            df[col]
            .astype(str)
            .str.replace(
                '"',
                "",
                regex=False
            )
            .str.replace(
                "\r",
                "",
                regex=False
            )
            .str.replace(
                "\n",
                "",
                regex=False
            )
            .str.strip()
        )

    # =============================
    # 🔴 COLUMNAS OBLIGATORIAS
    # =============================

    for col in COLUMNAS_OBLIGATORIAS:

        if col not in df.columns:

            errores.append(
                f"Falta columna obligatoria: {col}"
            )

    if errores:

        return None, errores, warnings

    # =============================
    # 🟡 COLUMNAS ESPERADAS
    # =============================

    for col in COLUMNAS_ESPERADAS:

        if col not in df.columns:

            warnings.append(
                f"Falta columna esperada: {col}"
            )

    # =============================
    # 🧪 INICIALIZACIÓN
    # =============================

    df["estado"] = "OK"

    df["detalle_error"] = ""

    # =============================
    # 💰 CONVERSIÓN DE MONTOS
    # =============================

    for col in [
        "Monto bruto venta",
        "Monto neto",
        "Impuestos",
        "Monto bruto pago"
    ]:

        if col in df.columns:

            # 🔥 si accidentalmente quedó duplicada
            if isinstance(df[col], pd.DataFrame):

                df[col] = df[col].iloc[:, 0]

            df[col] = (
                df[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
                .replace(
                    ["", "nan", "None"],
                    pd.NA
                )
            )

            df[col] = pd.to_numeric(
                df[col],
                errors="coerce"
            )

    # =============================
    # 🔁 VALIDACIÓN INTELIGENTE
    # =============================

    if "ID de venta" in df.columns:

        count = (
            df.groupby("ID de venta")
            ["ID de venta"]
            .transform("count")
        )

        # =============================
        # 💳 VALIDAR ID PAGO
        # =============================

        if "ID de pago" in df.columns:

            pagos_unicos = (
                df.groupby("ID de venta")
                ["ID de pago"]
                .transform("nunique")
            )

            mask_pago_dup = (
                (count > 1) &
                (pagos_unicos != count)
            )

            df.loc[
                mask_pago_dup,
                "estado"
            ] = "ERROR"

            df.loc[
                mask_pago_dup,
                "detalle_error"
            ] += (
                "ID de pago duplicado en misma venta; "
            )

        # =============================
        # 💰 VALIDAR MONTOS MULTIPAGO
        # =============================

        if all(col in df.columns for col in [
            "Monto bruto venta",
            "Monto bruto pago"
        ]):

            suma_pagos = (
                df.groupby("ID de venta")[
                    "Monto bruto pago"
                ]
                .transform("sum")
            )

            referencia_venta = (
                df.groupby("ID de venta")[
                    "Monto bruto venta"
                ]
                .transform("first")
            )

            mask_monto = (
                (count > 1) &
                (
                    abs(
                        suma_pagos - referencia_venta
                    ) > 1
                )
            )

            df.loc[
                mask_monto,
                "estado"
            ] = "ERROR"

            df.loc[
                mask_monto,
                "detalle_error"
            ] += (
                "Descuadre en montos por ID de venta; "
            )

    # =============================
    # 🧾 VALIDAR CUIT
    # =============================

    if "CUIT" in df.columns:

        cuit = (
            df["CUIT"]
            .astype(str)
            .str.strip()
        )

        mask_cuit = (
            cuit.isna() |
            cuit.isin([
                "",
                "nan",
                "None"
            ])
        )

        df.loc[
            mask_cuit,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_cuit,
            "detalle_error"
        ] += "CUIT vacío; "

    
    # =============================
    # 📅 VALIDAR FECHA
    # =============================

    if "Fecha" in df.columns:

        mask_fecha = (
            pd.to_datetime(
                df["Fecha"],
                errors="coerce"
            )
            .isna()
        )

        df.loc[
            mask_fecha,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_fecha,
            "detalle_error"
        ] += "Fecha inválida; "

    # =============================
    # 💰 MONTO INVÁLIDO
    # =============================

    if "Monto bruto venta" in df.columns:

        mask_importe = (
            df["Monto bruto venta"]
            .isna()
        )

        df.loc[
            mask_importe,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_importe,
            "detalle_error"
        ] += (
            "Monto bruto inválido o vacío; "
        )

    # =============================
    # 🔥 NORMALIZACIÓN LISTAS
    # =============================

    tipos_pago_validos = normalizar_lista(
        TIPOS_PAGO_VALIDOS
    )

    brands_validos = normalizar_lista(
        CARD_BRANDS_VALIDOS
    )

    platform_validos = normalizar_lista(
        PLATFORM_CODES_VALIDOS
    )

    # =============================
    # 📄 VALIDAR TIPO
    # =============================

    if "Tipo" in df.columns:

        tipos_validos = set(
            TIPOS_DOCUMENTO_VALIDOS
        )

        tipo = (
            df["Tipo"]
            .astype(str)
            .str.strip()
        )

        mask_tipo = (
            ~tipo.isin(
                tipos_validos
            )
        )

        df.loc[
            mask_tipo,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_tipo,
            "detalle_error"
        ] += "Tipo inválido; "

    # =============================
    # 💳 TIPO DE PAGO
    # =============================

    if "Tipo de pago" in df.columns:

        if isinstance(df["Tipo de pago"], pd.DataFrame):

            df["Tipo de pago"] = (
                df["Tipo de pago"]
                .iloc[:, 0]
            )

        df["Tipo de pago"] = (
            df["Tipo de pago"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        mask_pago = (
            df["Tipo de pago"].notna() &
            (df["Tipo de pago"] != "") &
            (
                ~df["Tipo de pago"]
                .isin(tipos_pago_validos)
            )
        )

        df.loc[
            mask_pago,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_pago,
            "detalle_error"
        ] += (
            "Tipo de pago inválido; "
        )

    # =============================
    # 💳 MARCA TARJETA
    # =============================

    if (
        "Marca de tarjeta" in df.columns and
        "Tipo de pago" in df.columns
    ):

        if isinstance(df["Marca de tarjeta"], pd.DataFrame):

            df["Marca de tarjeta"] = (
                df["Marca de tarjeta"]
                .iloc[:, 0]
            )

        df["Marca de tarjeta"] = (
            df["Marca de tarjeta"]
            .astype(str)
            .str.strip()
            .str.upper()
        )

        mask_aplica = (
            df["Tipo de pago"]
            .isin(["CREDIT", "DEBIT"])
        )

        mask_brand = (
            mask_aplica &
            df["Marca de tarjeta"].notna() &
            (df["Marca de tarjeta"] != "") &
            (
                ~df["Marca de tarjeta"]
                .isin(brands_validos)
            )
        )

        df.loc[
            mask_brand,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_brand,
            "detalle_error"
        ] += (
            "Marca de tarjeta inválida; "
        )

    # =============================
    # 🌐 PLATFORM CODE
    # =============================

    if "Codigo Plataforma Externa" in df.columns:

        if isinstance(
            df["Codigo Plataforma Externa"],
            pd.DataFrame
        ):

            df["Codigo Plataforma Externa"] = (
                df["Codigo Plataforma Externa"]
                .iloc[:, 0]
            )

        # 🔥 limpiar SOLO espacios
        df["Codigo Plataforma Externa"] = (
            df["Codigo Plataforma Externa"]
            .fillna("")
            .astype(str)
            .str.strip()
        )

        platform_validos = set(
            PLATFORM_CODES_VALIDOS
        )

        # 🔥 ignorar vacíos reales
        mask_platform = (
            ~df[
                "Codigo Plataforma Externa"
            ].isin([
                "",
                "nan",
                "None",
                "<NA>"
            ])
        ) & (
            ~df[
                "Codigo Plataforma Externa"
            ].isin(platform_validos)
        )

        df.loc[
            mask_platform,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_platform,
            "detalle_error"
        ] += (
            "Platform code inválido; "
        )


    # =============================
    # 🆔 VALIDAR ID DE PAGO
    # =============================

    if "ID de pago" in df.columns:

        mask_id_pago = (
            df["ID de pago"]
            .isna()
            |
            df["ID de pago"]
            .astype(str)
            .str.strip()
            .isin([
                "",
                "nan",
                "None",
                "<NA>"
            ])
        )

        df.loc[
            mask_id_pago,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_id_pago,
            "detalle_error"
        ] += (
            "ID de pago vacío; "
        )

    # =============================
    # 🧮 VALIDACIÓN CONTABLE
    # =============================

    if all(
        col in df.columns
        for col in [
            "Monto neto",
            "Impuestos",
            "Monto bruto venta"
        ]
    ):

        neto = df["Monto neto"]

        impuestos = df["Impuestos"]

        bruto = df["Monto bruto venta"]

        # 🔴 Valores vacíos
        mask_vacios = (
            neto.isna() |
            impuestos.isna() |
            bruto.isna()
        )

        df.loc[
            mask_vacios,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_vacios,
            "detalle_error"
        ] += (
            "Monto neto, impuestos o bruto vacío; "
        )

        # 🔴 impuestos = 0
        mask_sin_impuestos = (
            (~mask_vacios) &
            (impuestos == 0) &
            (abs(neto - bruto) > 1)
        )

        df.loc[
            mask_sin_impuestos,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_sin_impuestos,
            "detalle_error"
        ] += (
            "Si impuestos es 0, neto debe ser igual al bruto; "
        )

        # 🔴 validación estándar
        mask_mismatch = (
            (~mask_vacios) &
            (
                abs(
                    (neto + impuestos) - bruto
                ) > 1
            )
        )

        df.loc[
            mask_mismatch,
            "estado"
        ] = "ERROR"

        df.loc[
            mask_mismatch,
            "detalle_error"
        ] += (
            "Descuadre: Neto + Impuestos ≠ Bruto; "
        )

    return df, errores, warnings