def completitud(df, col):
    if col not in df.columns:
        return 0
    total = len(df)
    validos = df[col].notna() & (df[col] != "")
    return (validos.sum() / total) * 100


def sugerir_reglas(df):
    c = {col: completitud(df, col) for col in df.columns}

    resultado = {}

    # ===== CAMPOS =====
    cup = c.get("Voucher", 0)
    auth = c.get("Codigo de autorizacion", 0)
    tarjeta = c.get("Numero de tarjeta", 0)
    marca = c.get("Marca de tarjeta", 0)
    tipo = c.get("Tipo de pago", 0)
    ref = c.get("Referencia externa", 0)

    # ===== 🟢 ESTRICTA =====
    if all(x > 80 for x in [cup, auth, tarjeta, marca, tipo]):
        resultado["estricta"] = {
            "ok": True,
            "campos": [
                "Monto bruto venta",
                "Tipo de pago",
                "Marca de tarjeta",
                "Numero de tarjeta",
                "Voucher",
                "Codigo de autorizacion",
                "Fecha"
            ],
            "tolerancia": "Sin tolerancia o mínima"
        }
    else:
        resultado["estricta"] = {
            "ok": False,
            "motivo": "Falta completitud en campos clave (cupón, autorización, tarjeta, marca o tipo de pago)"
        }

    # ===== 🟡 INTERMEDIA =====
    if all(x > 70 for x in [cup, marca, tipo]):
        resultado["intermedia"] = {
            "ok": True,
            "campos": [
                "Monto bruto venta",
                "Tipo de pago",
                "Marca de tarjeta",
                "Voucher",
                "Fecha"
            ],
            "tolerancia": "Monto: $1-2 | Fecha: ±24hs"
        }
    else:
        resultado["intermedia"] = {
            "ok": False,
            "motivo": "No hay suficiente calidad en cupón, marca o tipo de pago"
        }

    # ===== 🔵 FLEXIBLE =====
    campos_flex = ["Monto bruto venta", "Fecha"]

    if ref > 50:
        campos_flex.append("Referencia externa")

    resultado["flexible"] = {
        "ok": True,
        "campos": campos_flex,
        "tolerancia": "Monto: $1-2 | Fecha: ±24hs"
    }

    return resultado