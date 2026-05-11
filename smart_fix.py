import os
import json
import pandas as pd

ARCHIVO_APRENDIZAJES = "aprendizajes.json"


# =============================
# 📚 CARGAR APRENDIZAJES
# =============================

def cargar_aprendizajes():

    if not os.path.exists(ARCHIVO_APRENDIZAJES):

        return {}

    with open(
        ARCHIVO_APRENDIZAJES,
        "r",
        encoding="utf-8"
    ) as f:

        contenido = f.read().strip()

        if not contenido:

            return {}

        return json.loads(contenido)


# =============================
# 💾 GUARDAR APRENDIZAJES
# =============================

def guardar_aprendizajes(data):

    with open(
        ARCHIVO_APRENDIZAJES,
        "w",
        encoding="utf-8"
    ) as f:

        json.dump(
            data,
            f,
            ensure_ascii=False,
            indent=4
        )


# =============================
# 🔎 DETECTAR INVÁLIDOS
# =============================

def detectar_valores_invalidos(
    df,
    columna,
    valores_validos
):

    if columna not in df.columns:

        return []

    # 🔥 normalizar válidos
    valores_validos = set(
        str(x).strip().upper()
        for x in valores_validos
    )

    # 🔥 eliminar nulos reales
    serie = df[columna].dropna()

    # 🔥 normalizar valores
    serie = (
        serie
        .astype(str)
        .str.strip()
        .str.upper()
    )

    # 🔥 ignorar vacíos reales
    serie = serie[
        serie != ""
    ]

    # 🔥 obtener inválidos reales
    invalidos = serie[
        ~serie.isin(valores_validos)
    ].unique()

    return list(invalidos)


# =============================
# 🔧 APLICAR CORRECCIÓN
# =============================

def aplicar_correccion(
    df,
    columna,
    valor_original,
    nuevo_valor,
    aplicar_masivo=True
):

    if columna not in df.columns:

        return df

    if aplicar_masivo:

        mask = (
            df[columna]
            .astype(str)
            .str.upper()
            .str.strip()
            == str(valor_original).upper().strip()
        )

        df.loc[
            mask,
            columna
        ] = nuevo_valor

    else:

        mask = (
            df[columna]
            .astype(str)
            .str.upper()
            .str.strip()
            == str(valor_original).upper().strip()
        )

        if mask.any():

            primer_indice = (
                df[mask]
                .index[0]
            )

            df.loc[
                primer_indice,
                columna
            ] = nuevo_valor

    return df


# =============================
# 🧠 GUARDAR SUGERENCIA
# =============================

def guardar_sugerencia(
    columna,
    valor_original,
    nuevo_valor
):

    data = cargar_aprendizajes()

    if columna not in data:

        data[columna] = {}

    data[columna][valor_original] = nuevo_valor

    guardar_aprendizajes(data)


# =============================
# 📚 OBTENER SUGERENCIA
# =============================

def obtener_sugerencia(
    columna,
    valor_original
):

    data = cargar_aprendizajes()

    if columna not in data:

        return None

    return data[columna].get(
        valor_original
    )