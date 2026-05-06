import pandas as pd
from config import (
    COLUMNAS_OBLIGATORIAS,
    COLUMNAS_ESPERADAS,
    CARD_BRANDS_VALIDOS,
    PLATFORM_CODES_VALIDOS,
    TIPOS_PAGO_VALIDOS
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
    return set(normalizar_texto(x) for x in lista)


def validar_archivo(df):
    errores = []
    warnings = []

    if not isinstance(df, pd.DataFrame):
        return None, ["El archivo no pudo ser procesado correctamente"], []

    df.columns = df.columns.str.strip()
    df = df.copy()

    # 🔴 Columnas obligatorias
    for col in COLUMNAS_OBLIGATORIAS:
        if col not in df.columns:
            errores.append(f"Falta columna obligatoria: {col}")

    if errores:
        return None, errores, warnings

    # 🟡 Columnas esperadas
    for col in COLUMNAS_ESPERADAS:
        if col not in df.columns:
            warnings.append(f"Falta columna esperada: {col}")

    # 🧪 Inicialización
    df["estado"] = "OK"
    df["detalle_error"] = ""

    # 🔥 CONVERSIÓN DE MONTOS (UNA SOLA VEZ)
    for col in ["Monto bruto venta", "Monto neto", "Impuestos"]:
        if col in df.columns:
            df[col] = (
                df[col]
                .astype(str)
                .str.replace(".", "", regex=False)
                .str.replace(",", ".", regex=False)
            )
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # 🔁 VALIDACIÓN INTELIGENTE (VECTORIAL)
    if "ID de venta" in df.columns:

        count = df.groupby("ID de venta")["ID de venta"].transform("count")

        if "ID de pago" in df.columns:
            pagos_unicos = df.groupby("ID de venta")["ID de pago"].transform("nunique")

            mask_pago_dup = (count > 1) & (pagos_unicos != count)

            df.loc[mask_pago_dup, "estado"] = "ERROR"
            df.loc[mask_pago_dup, "detalle_error"] += "ID de pago duplicado en misma venta; "

        if "Monto bruto venta" in df.columns:
            suma = df.groupby("ID de venta")["Monto bruto venta"].transform("sum")
            referencia = df.groupby("ID de venta")["Monto bruto venta"].transform("first")

            mask_monto = (count > 1) & (abs(suma - referencia) > 1)

            df.loc[mask_monto, "estado"] = "ERROR"
            df.loc[mask_monto, "detalle_error"] += "Descuadre en montos por ID de venta; "

    # 📅 Fecha
    if "Fecha" in df.columns:
        mask_fecha = pd.to_datetime(df["Fecha"], errors="coerce").isna()
        df.loc[mask_fecha, "estado"] = "ERROR"
        df.loc[mask_fecha, "detalle_error"] += "Fecha inválida; "

    # 💰 Monto inválido
    if "Monto bruto venta" in df.columns:
        mask_importe = df["Monto bruto venta"].isna()
        df.loc[mask_importe, "estado"] = "ERROR"
        df.loc[mask_importe, "detalle_error"] += "Monto inválido; "

    # 🔥 Normalización listas
    tipos_pago_validos = normalizar_lista(TIPOS_PAGO_VALIDOS)
    brands_validos = normalizar_lista(CARD_BRANDS_VALIDOS)
    platform_validos = normalizar_lista(PLATFORM_CODES_VALIDOS)

    # 💳 Tipo de pago
    if "Tipo de pago" in df.columns:
        df["Tipo de pago"] = df["Tipo de pago"].astype(str).str.strip().str.upper()

        mask_pago = (
            df["Tipo de pago"].notna() &
            (df["Tipo de pago"] != "") &
            (~df["Tipo de pago"].isin(tipos_pago_validos))
        )

        df.loc[mask_pago, "estado"] = "ERROR"
        df.loc[mask_pago, "detalle_error"] += "Tipo de pago inválido; "

    # 💳 Marca de tarjeta
    if "Marca de tarjeta" in df.columns and "Tipo de pago" in df.columns:

        df["Marca de tarjeta"] = df["Marca de tarjeta"].astype(str).str.strip().str.upper()

        mask_aplica = df["Tipo de pago"].isin(["CREDIT", "DEBIT"])

        mask_brand = (
            mask_aplica &
            df["Marca de tarjeta"].notna() &
            (df["Marca de tarjeta"] != "") &
            (~df["Marca de tarjeta"].isin(brands_validos))
        )

        df.loc[mask_brand, "estado"] = "ERROR"
        df.loc[mask_brand, "detalle_error"] += "Marca de tarjeta inválida; "

    # 🌐 Platform code
    if "Codigo Plataforma Externa" in df.columns:
        df["Codigo Plataforma Externa"] = df["Codigo Plataforma Externa"].astype(str).str.strip().str.upper()

        mask_platform = (
            df["Codigo Plataforma Externa"].notna() &
            (df["Codigo Plataforma Externa"] != "") &
            (~df["Codigo Plataforma Externa"].isin(platform_validos))
        )

        df.loc[mask_platform, "estado"] = "ERROR"
        df.loc[mask_platform, "detalle_error"] += "Platform code inválido; "

    # 🧮 Validación contable
    if all(col in df.columns for col in ["Monto neto", "Impuestos", "Monto bruto venta"]):

        neto = df["Monto neto"]
        impuestos = df["Impuestos"]
        bruto = df["Monto bruto venta"]

        mask_mismatch = abs((neto + impuestos) - bruto) > 1

        df.loc[mask_mismatch, "estado"] = "ERROR"
        df.loc[mask_mismatch, "detalle_error"] += "Descuadre: Neto + Impuestos ≠ Bruto; "

    return df, errores, warnings