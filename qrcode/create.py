import segno

qr = segno.make("https://github.com/JadKHaddad/ALPS", error="h")
qr.save("qrcode.pdf", scale=10, border=4)
