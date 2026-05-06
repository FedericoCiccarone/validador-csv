# config.py

# 🔴 Columnas obligatorias
COLUMNAS_OBLIGATORIAS = [
    "ID de venta",
    "Fecha",
    "Monto bruto venta",
    "Tipo de pago"
]


# 🟡 Columnas esperadas
COLUMNAS_ESPERADAS = [
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


# 💳 Card Brands válidos
CARD_BRANDS_VALIDOS = [
     "ACCOR",
    "AMEX",
    "ANDA CREDIT",
    "ANK",
    "ARGENCARD",
    "BILLETERA SANTA FE",
    "BM CIUDAD",
    "BNA PLUS",
    "CABAL",
    "CABAL DEBIT",
    "CDNI",
    "CENTROCARD",
    "CLARO PAY",
    "CONSUMAX",
    "CREDENCIAL MBARETE",
    "CREDICASH",
    "CREDITOS DIRECTOS",
    "DINAMICA",
    "DINERS CLUB",
    "DISCOVER",
    "FALABELLA CMR",
    "ITALCRED",
    "LOCRED",
    "MAESTRO",
    "MAESTRO DEBIT",
    "MASTERCARD",
    "MASTERCARD DEBIT",
    "MERCADO PAGO",
    "MODO",
    "MONI ONLINE",
    "NARANJA",
    "NARANJA DEBIT",
    "NATIVA",
    "NOA EXPRESS",
    "OCA",
    "OTHER",
    "PASSCARD",
    "POSNET CELULAR",
    "REBA",
    "RED LIDER",
    "RESIMPLE",
    "SOL",
    "SUCREDITO",
    "SUPER DIGITAL",
    "TARJETA MAS",
    "TICKET NACION",
    "TITANIO",
    "TUYA CREDITO",
    "TUYA PREPAGA",
    "UALA",
    "UNICA",
    "UNION PAY",
    "VALEPEI",
    "VISA",
    "VISA DEBIT",
    "VISA PREPAGA",
    "YACARE QR"
]


# 🌐 Platform External Code válidos
PLATFORM_CODES_VALIDOS = [
    "accor_ar","amex_ar","bilsantafe_ar","cabal_ar","firstdata_ar",
    "getnet_ar","gocuotas_ar","italcred_ar","mercadopago_ar","naranja_ar",
    "pedidosya_ar","prisma_ar","rappi_ar","tiendanube_ar",
    "citi_co","colpatria_co","didi_co","diners_co","mercadopago_co","rappi_co",
    "amex_uy","anda_uy","cabal_uy","cdirectos_uy","creditel_uy","dlocal_uy",
    "edenred_uy","firstdata_uy","mercadopago_uy","oca_uy","passcard_uy",
    "pedidosya_uy","rappi_uy","visanet_uy"
]


# 💰 Tipos de pago válidos
TIPOS_PAGO_VALIDOS = [
    "cash",
    "debit",
    "credit",
    "qr",
    "wallet"
]