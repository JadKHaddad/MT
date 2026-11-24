import segno

qr = segno.make(
    "https://github.com/JadKHaddad/ALPS/tree/0fe669cdc154f0b48cad1f8a21fb59b4d47322a3",
    error="h",
)
qr.save("qrcode.pdf", scale=10, border=4)
